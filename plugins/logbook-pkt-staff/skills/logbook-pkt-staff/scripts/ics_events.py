#!/usr/bin/env python3
"""Baca satu/lebih file .ics -> events.json untuk rentang tanggal tertentu.

Pemakaian:
  python ics_events.py --start 2026-11-02 --end 2026-11-30 --ics a.ics [b.ics ...] \
      [--email saya@contoh.id] --out events.json

Hanya judul dan waktu yang dibaca. Deskripsi, lokasi, dan peserta tidak disimpan.
Semua waktu dikonversi ke WIB (Asia/Jakarta); tanggal ditentukan dari waktu mulai di WIB.
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from dateutil.rrule import rrulestr, rruleset
except ImportError:
    sys.exit("Modul python-dateutil belum ada: pip install python-dateutil")

WIB = ZoneInfo("Asia/Jakarta")
UTC = timezone.utc
WIN_TZ = {
    "SE Asia Standard Time": "Asia/Jakarta",
    "Singapore Standard Time": "Asia/Singapore",
    "Tokyo Standard Time": "Asia/Tokyo",
    "GMT Standard Time": "Europe/London",
    "W. Europe Standard Time": "Europe/Berlin",
    "Eastern Standard Time": "America/New_York",
    "Pacific Standard Time": "America/Los_Angeles",
    "UTC": "UTC",
}
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
NON_KERJA = re.compile(
    r"\b(lunch|makan siang|istirahat|break|reminder|pengingat|focus time|blok fokus|"
    r"busy|do not book|jumatan|birthday|ulang tahun|ultah)\b", re.I)
CUTI = re.compile(r"\b(cuti|leave|izin|ooo|out of office|libur|sakit|vacation|holiday)\b", re.I)
AMBIGU = {"meeting", "rapat", "busy", "block", "hold", "call", "tentative", "event", "agenda"}
KAL_LIBUR = re.compile(r"holiday|hari libur|libur nasional", re.I)
CUTI_BERSAMA = re.compile(r"cuti bersama|collective leave", re.I)


# ---------- parsing ICS ----------
def unfold(text):
    out = []
    for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if ln[:1] in (" ", "\t") and out:
            out[-1] += ln[1:]
        else:
            out.append(ln)
    return out


def split_outside_quotes(s, sep):
    parts, cur, inq = [], "", False
    for ch in s:
        if ch == '"':
            inq = not inq
        if ch == sep and not inq:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def split_prop(line):
    inq = False
    for i, ch in enumerate(line):
        if ch == '"':
            inq = not inq
        elif ch == ":" and not inq:
            head, val = line[:i], line[i + 1:]
            break
    else:
        return None
    bits = split_outside_quotes(head, ";")
    params = {}
    for p in bits[1:]:
        k, _, v = p.partition("=")
        params[k.upper()] = v.strip('"')
    return bits[0].upper(), params, val


def unescape(v):
    return (v.replace("\\n", " ").replace("\\N", " ").replace("\\,", ",")
             .replace("\\;", ";").replace("\\\\", "\\").strip())


def parse_dt(val, params, warns):
    val = val.strip()
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", val):
        return date(int(val[:4]), int(val[4:6]), int(val[6:8]))
    m = re.fullmatch(r"(\d{8})T(\d{6})(Z?)", val)
    if not m:
        return None
    d = datetime.strptime(m[1] + m[2], "%Y%m%d%H%M%S")
    if m[3]:
        return d.replace(tzinfo=UTC)
    tzid = params.get("TZID")
    if not tzid:
        return d.replace(tzinfo=WIB)
    try:
        return d.replace(tzinfo=ZoneInfo(WIN_TZ.get(tzid, tzid)))
    except Exception:
        warns.add(f"Zona waktu '{tzid}' tidak dikenal; waktu dianggap WIB")
        return d.replace(tzinfo=WIB)


def parse_duration(v):
    m = re.fullmatch(r"P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", v.strip())
    if not m:
        return None
    w, d, h, mi, s = (int(x or 0) for x in m.groups())
    return timedelta(weeks=w, days=d, hours=h, minutes=mi, seconds=s)


def read_ics(path, extra_emails, warns):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    calname, events, cur = "", [], None
    for line in unfold(text):
        if line.upper() == "BEGIN:VEVENT":
            cur = {"attendees": [], "exdates": []}
            continue
        if line.upper() == "END:VEVENT":
            if cur is not None:
                events.append(cur)
            cur = None
            continue
        p = split_prop(line)
        if not p:
            continue
        name, params, val = p
        if cur is None:
            if name == "X-WR-CALNAME":
                calname = unescape(val)
            continue
        if name == "SUMMARY":
            cur["summary"] = unescape(val)
        elif name == "UID":
            cur["uid"] = val.strip()
        elif name == "DTSTART":
            cur["dtstart"] = parse_dt(val, params, warns)
        elif name == "DTEND":
            cur["dtend"] = parse_dt(val, params, warns)
        elif name == "DURATION":
            cur["duration"] = parse_duration(val)
        elif name == "STATUS":
            cur["status"] = val.strip().upper()
        elif name == "TRANSP":
            cur["transp"] = val.strip().upper()
        elif name == "RRULE":
            cur["rrule"] = val.strip()
        elif name == "EXDATE":
            for v in val.split(","):
                d = parse_dt(v, params, warns)
                if d is not None:
                    cur["exdates"].append(d)
        elif name == "RECURRENCE-ID":
            cur["recurrence_id"] = parse_dt(val, params, warns)
        elif name == "ATTENDEE":
            cur["attendees"].append((val.lower().replace("mailto:", "").strip(),
                                     params.get("PARTSTAT", "").upper()))
    owners = {e.lower() for e in extra_emails}
    if "@" in calname:
        owners.add(calname.lower().strip())
    return calname, owners, events


# ---------- ekspansi jadwal berulang ----------
def is_date(x):
    return isinstance(x, date) and not isinstance(x, datetime)


def key_of(x):
    return x.isoformat() if is_date(x) else int(x.astimezone(UTC).timestamp())


def occurrences(ev, lo, hi, warns):
    s = ev["dtstart"]
    rule = ev.get("rrule")
    if not rule:
        return [s]
    base = datetime(s.year, s.month, s.day) if is_date(s) else s

    def fix_until(m):
        u = m.group(1)
        if base.tzinfo is not None:
            u = u + "T235959Z" if "T" not in u else (u if u.endswith("Z") else u + "Z")
        else:
            u = u.rstrip("Z")
        return "UNTIL=" + u

    rule = re.sub(r"UNTIL=([0-9TZ]+)", fix_until, rule)
    try:
        rs = rruleset()
        rs.rrule(rrulestr(rule, dtstart=base))
        for ex in ev["exdates"]:
            rs.exdate(datetime(ex.year, ex.month, ex.day) if is_date(ex) else ex)
        if base.tzinfo is not None:
            lo_, hi_ = lo.astimezone(base.tzinfo), hi.astimezone(base.tzinfo)
        else:
            lo_, hi_ = lo.replace(tzinfo=None), hi.replace(tzinfo=None)
        got = rs.between(lo_, hi_, inc=True)
    except Exception as e:
        warns.add(f"Jadwal berulang '{ev.get('summary', '')}' gagal dibaca ({e}); dianggap sekali")
        return [s]
    return [o.date() if is_date(s) else o for o in got]


def normalisasi(t):
    return re.sub(r"\s+", " ", t.strip().lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--ics", nargs="+", required=True)
    ap.add_argument("--email", nargs="*", default=[])
    ap.add_argument("--out", default="events.json")
    a = ap.parse_args()
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    if end < start:
        sys.exit("tanggal_selesai < tanggal_mulai")

    lo = datetime(start.year, start.month, start.day, tzinfo=WIB) - timedelta(days=2)
    hi = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=WIB) + timedelta(days=2)
    warns, pemilik = set(), set()
    mentah, di_luar = [], 0
    libur_kand, cuti_bersama_kand, cuti_kand = {}, {}, {}

    for path in a.ics:
        calname, owners, events = read_ics(path, a.email, warns)
        pemilik |= owners
        if not owners:
            warns.add(f"{Path(path).name}: email pemilik tidak diketahui; status 'tolak' tidak bisa dicek")
        is_holiday_cal = bool(KAL_LIBUR.search(calname))
        overrides = {(e.get("uid"), key_of(e["recurrence_id"]))
                     for e in events if e.get("recurrence_id") is not None and e.get("dtstart") is not None}
        for ev in events:
            s = ev.get("dtstart")
            if s is None:
                continue
            judul = ev.get("summary", "").strip()
            allday = is_date(s)
            if "dtend" in ev and ev["dtend"] is not None:
                e = ev["dtend"]
            elif ev.get("duration") is not None and not allday:
                e = s + ev["duration"]
            else:
                e = s + timedelta(days=1) if allday else s
            dur = (e - s) if not (allday and is_date(e)) else timedelta(days=(e - s).days)
            partstat = ""
            for em, ps in ev["attendees"]:
                if em in owners:
                    partstat = ps
            status = ev.get("status", "")
            is_override = ev.get("recurrence_id") is not None
            for occ in occurrences(ev, lo, hi, warns):
                if not is_override and (ev.get("uid"), key_of(occ)) in overrides:
                    continue
                if allday:
                    days = [occ + timedelta(n) for n in range(max(dur.days, 1))]
                    for d in days:
                        if not start <= d <= end:
                            di_luar += 1
                            continue
                        if status == "CANCELLED" or partstat == "DECLINED":
                            continue
                        if is_holiday_cal:
                            target = cuti_bersama_kand if CUTI_BERSAMA.search(judul) else libur_kand
                            target[d.isoformat()] = judul
                        elif CUTI.search(judul):
                            cuti_kand[d.isoformat()] = judul
                        else:
                            mentah.append({"tgl": d, "mulai": None, "selesai": None, "judul": judul,
                                           "sumber": calname, "alasan": "acara sehari penuh (bukan kegiatan berjam)"})
                    continue
                ws = occ.astimezone(WIB)
                we = (occ + dur).astimezone(WIB)
                if not start <= ws.date() <= end:
                    di_luar += 1
                    continue
                rec = {"tgl": ws.date(), "mulai": ws, "selesai": we, "judul": judul, "sumber": calname,
                       "flags": [], "alasan": None}
                if status == "CANCELLED":
                    rec["alasan"] = "dibatalkan (cancelled)"
                elif partstat == "DECLINED":
                    rec["alasan"] = "ditolak (declined)"
                else:
                    if partstat == "TENTATIVE" or status == "TENTATIVE":
                        rec["flags"].append("tentatif")
                    if ev.get("transp") == "TRANSPARENT":
                        rec["flags"].append("ditandai 'free' di kalender")
                    if NON_KERJA.search(judul):
                        rec["flags"].append("kemungkinan bukan kegiatan kerja")
                    if ws.hour < 6 or ws.hour >= 20:
                        rec["flags"].append("di luar jam kerja (sebelum 06:00 / sesudah 20:00)")
                    if we.date() != ws.date():
                        rec["flags"].append("melewati tengah malam (dicatat di hari mulai)")
                    if we <= ws:
                        rec["flags"].append("tanpa durasi")
                    if normalisasi(judul) in AMBIGU or len(judul) < 4:
                        rec["flags"].append("judul ambigu")
                mentah.append(rec)

    # gabung duplikat (kalender berbeda, waktu dan judul sama)
    kandidat, dikecualikan, dedup, dup_count = [], [], {}, 0
    for r in sorted(mentah, key=lambda x: (x["tgl"], x["mulai"] or datetime.min.replace(tzinfo=WIB), x["judul"])):
        if r["alasan"]:
            dikecualikan.append(r)
            continue
        k = (r["tgl"], r["mulai"], normalisasi(r["judul"]))
        if k in dedup:
            dedup[k]["flags"].append("duplikat digabung")
            dup_count += 1
            continue
        dedup[k] = r
        kandidat.append(r)

    # bentrok
    for i, x in enumerate(kandidat):
        for y in kandidat[i + 1:]:
            if y["mulai"] >= x["selesai"] and y["tgl"] != x["tgl"]:
                break
            if y["tgl"] == x["tgl"] and y["mulai"] < x["selesai"] and x["mulai"] < y["selesai"]:
                x.setdefault("bentrok_dengan", []).append(y["judul"])
                y.setdefault("bentrok_dengan", []).append(x["judul"])

    def out_rec(r, idx=None):
        o = {"tanggal": r["tgl"].isoformat(), "hari": HARI[r["tgl"].weekday()],
             "mulai": r["mulai"].strftime("%H:%M") if r["mulai"] else None,
             "selesai": r["selesai"].strftime("%H:%M") if r["selesai"] else None,
             "judul": r["judul"] or "(tanpa judul)"}
        if idx is not None:
            o["id"] = idx
            o["catatan"] = list(r.get("flags", []))
            if r.get("bentrok_dengan"):
                o["catatan"].append("bentrok dengan: " + "; ".join(r["bentrok_dengan"]))
        else:
            o["alasan"] = r["alasan"]
        return o

    hasil = {
        "rentang": {"mulai": start.isoformat(), "selesai": end.isoformat(), "zona_waktu": "Asia/Jakarta"},
        "pemilik_terdeteksi": sorted(pemilik),
        "peringatan_baca": sorted(warns),
        "kandidat": [out_rec(r, i + 1) for i, r in enumerate(kandidat)],
        "dikecualikan": [out_rec(r) for r in dikecualikan],
        "libur_kandidat_dari_ics": dict(sorted(libur_kand.items())),
        "cuti_bersama_kandidat_dari_ics": dict(sorted(cuti_bersama_kand.items())),
        "cuti_pribadi_kandidat": dict(sorted(cuti_kand.items())),
        "duplikat_digabung": dup_count,
        "di_luar_rentang": di_luar,
    }
    Path(a.out).write_text(json.dumps(hasil, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"out": a.out, "kandidat": len(kandidat), "dikecualikan": len(dikecualikan),
                      "cuti_pribadi_kandidat": len(cuti_kand), "libur_kandidat": len(libur_kand) + len(cuti_bersama_kand),
                      "duplikat_digabung": dup_count, "di_luar_rentang": di_luar,
                      "peringatan_baca": sorted(warns)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
