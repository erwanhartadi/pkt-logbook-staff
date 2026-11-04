#!/usr/bin/env python3
"""Uji pemotong-kalender.html (via Node) dengan data FIKTIF.

Kalender sintetis multi-tahun dipotong ke satu rentang, lalu hasil pembacaan skill
(ics_events.py) dari kalender penuh dan kalender terpotong harus identik.
Juga memeriksa: ukuran mengecil, deskripsi/peserta lain terbuang, zip valid.
Cetak 'OK' bila lolos. Butuh: node >= 20.
"""
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "dist" / "pemotong-kalender.html"
HARNESS = Path(__file__).resolve().parent / "run_pemotong.mjs"
ICS_EVENTS = ROOT / "plugins/logbook-pkt-staff/skills/logbook-pkt-staff/scripts/ics_events.py"
OWNER = "staf.contoh@example.test"
START, END = "2026-11-02", "2026-11-20"
SECRET = "RAHASIA-XYZ"

TZ_BLOCK = """BEGIN:VTIMEZONE
TZID:Asia/Jakarta
BEGIN:STANDARD
TZOFFSETFROM:+0700
TZOFFSETTO:+0700
TZNAME:WIB
DTSTART:19700101T000000
END:STANDARD
END:VTIMEZONE"""


def ev(uid, summary, start, end=None, extra=(), owner_ps=None, allday=False, tz="Asia/Jakarta", duration=None):
    L = ["BEGIN:VEVENT", f"UID:{uid}"]
    if allday:
        L.append(f"DTSTART;VALUE=DATE:{start}")
        if end:
            L.append(f"DTEND;VALUE=DATE:{end}")
    else:
        pre = "DTSTART:" if start.endswith("Z") or tz is None else f"DTSTART;TZID={tz}:"
        L.append(pre + start)
        if end:
            L.append(("DTEND:" if end.endswith("Z") or tz is None else f"DTEND;TZID={tz}:") + end)
        if duration:
            L.append(f"DURATION:{duration}")
    L.append(f"SUMMARY:{summary}")
    L += list(extra)
    L += [f"DESCRIPTION:{SECRET} catatan pribadi", "LOCATION:Ruang rahasia",
          "ORGANIZER;CN=Orang Lain:mailto:ana@example.test",
          'ATTENDEE;CN="Dr. Ana: Jaya";PARTSTAT=ACCEPTED:mailto:ana@example.test']
    if owner_ps:
        L.append(f'ATTENDEE;CUTYPE=INDIVIDUAL;PARTSTAT={owner_ps};CN="Staf: Contoh":mailto:{OWNER}')
    L += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{SECRET} alarm", "TRIGGER:-PT10M", "END:VALARM", "END:VEVENT"]
    return "\n".join(L)


def lipat(summary):
    """Lipat baris ICS (75 karakter) untuk menguji unfold."""
    line = f"SUMMARY:{summary}"
    return line[:75] + "".join("\r\n " + line[i:i + 74] for i in range(75, len(line), 74))


def cal(name, body):
    return f"BEGIN:VCALENDAR\nVERSION:2.0\nX-WR-CALNAME:{name}\n{TZ_BLOCK}\n" + "\n".join(body) + "\nEND:VCALENDAR\n"


def kalender_kerja():
    b = []
    d0 = date(2019, 1, 1)
    for i in range(1500):  # riwayat lama
        d = d0 + timedelta(days=int(i * 1.7))
        b.append(ev(f"old{i}", f"Agenda lama {i}", d.strftime("%Y%m%d") + "T090000", d.strftime("%Y%m%d") + "T100000", owner_ps="ACCEPTED"))
    b += [
        ev("e1", "Rapat koordinasi tim", "20261102T090000", "20261102T100000"),
        ev("e2", "Diskusi proposal", "20261102T093000", "20261102T103000"),
        ev("e3", "Webinar kesehatan", "20261103T060000Z", "20261103T070000Z"),
        ev("e4", "Lunch", "20261103T120000", "20261103T130000"),
        ev("e5", "Rapat yang ditolak", "20261104T100000", "20261104T110000", owner_ps="DECLINED"),
        ev("e6", "Rapat dibatalkan", "20261104T130000", "20261104T140000", extra=["STATUS:CANCELLED"]),
        ev("e7", "Cuti tahunan", "20261105", "20261106", allday=True),
        ev("e8", "Konsultasi daring luar negeri", "20261105T220000", "20261105T230000", tz="America/New_York"),
        ev("e9", "Diskusi tentatif", "20261109T140000", "20261109T150000", owner_ps="TENTATIVE"),
        ev("e10", "Pengolahan data malam", "20261110T230000", "20261110T233000"),
        ev("e11", "Meeting", "20261111T090000", "20261111T100000"),
        ev("e12", "Kerja akhir pekan", "20261107T100000", "20261107T110000"),
        ev("e13", "Acara tanpa zona waktu", "20261113T090000", "20261113T100000", tz=None),
        ev("e14", "Acara dengan durasi", "20261113T140000", duration="PT1H30M"),
        ev("e15", "Cuti panjang", "20261030", "20261104", allday=True),
        # jadwal berulang
        ev("w1", "Weekly sync", "20260105T080000", "20260105T083000",
           extra=["RRULE:FREQ=WEEKLY;BYDAY=MO", "EXDATE;TZID=Asia/Jakarta:20261109T080000"]),
        ev("w1", "Weekly sync (dipindah)", "20261116T100000", "20261116T103000",
           extra=["RECURRENCE-ID;TZID=Asia/Jakarta:20261116T080000"]),
        ev("w2", "Sinkronisasi", "20260106T100000", "20260106T110000", extra=["RRULE:FREQ=WEEKLY;BYDAY=TU"]),
        ev("w2", "Sinkronisasi (dipindah ke Desember)", "20261215T100000", "20261215T110000",
           extra=["RECURRENCE-ID;TZID=Asia/Jakarta:20261110T100000"]),
        ev("w3", "Rutin lama", "20200106T100000", "20200106T110000", extra=["RRULE:FREQ=WEEKLY;UNTIL=20221231T000000Z"]),
        ev("w4", "Pelatihan 2019", "20190107T100000", "20190107T110000", extra=["RRULE:FREQ=WEEKLY;COUNT=3"]),
        ev("w5", "Rapat bulanan", "20260101T130000", "20260101T140000", extra=["RRULE:FREQ=MONTHLY;BYMONTHDAY=18;UNTIL=20271231"]),
    ]
    b.append("\n".join(["BEGIN:VEVENT", "UID:e16", "DTSTART;TZID=Asia/Jakarta:20261112T080000",
                        "DTEND;TZID=Asia/Jakarta:20261112T090000",
                        lipat("Rapat dengan judul yang sangat panjang sekali supaya terlipat pada baris ICS standar ya"),
                        "END:VEVENT"]))
    return cal(OWNER, b)


def kalender_pribadi():
    return cal("Pribadi", [
        ev("p1", "Olahraga pagi", "20200101T060000", "20200101T070000", extra=["RRULE:FREQ=DAILY"]),
        ev("p2", "Acara tahun lalu", "20231005T090000", "20231005T100000"),
    ])


def kalender_libur():
    return cal("Holidays in Indonesia", [
        ev("h1", "Hari Contoh Libur", "20261112", "20261113", allday=True),
        ev("h2", "Libur lama", "20230817", "20230818", allday=True),
    ])


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"GAGAL: {' '.join(map(str, cmd[:3]))}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def ics_json(src, out):
    run([sys.executable, "-I", ICS_EVENTS, "--start", START, "--end", END, "--ics", *src, "--out", out])
    return json.loads(Path(out).read_text(encoding="utf-8"))


def norm(d):
    keys = ["kandidat", "dikecualikan", "cuti_pribadi_kandidat", "libur_kandidat_dari_ics",
            "cuti_bersama_kandidat_dari_ics", "duplikat_digabung", "pemilik_terdeteksi"]
    return {k: d[k] for k in keys}


def check(cond, msg):
    if not cond:
        sys.exit(f"GAGAL: {msg}")


def main():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        isi = {f"{OWNER}.ics": kalender_kerja(), "Pribadi.ics": kalender_pribadi(), "Holidays in Indonesia.ics": kalender_libur()}
        raw_dir = t / "raw"
        raw_dir.mkdir()
        for n, txt in isi.items():
            (raw_dir / n).write_text(txt, encoding="utf-8")
        full_zip = t / "calendar-export.zip"
        with zipfile.ZipFile(full_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for n, txt in isi.items():
                z.writestr(n, txt)
        full_bytes = sum(len(x.encode()) for x in isi.values())

        base = ics_json([full_zip], t / "full.json")
        check(len(base["kandidat"]) > 10, "uji tidak bermakna: kandidat terlalu sedikit")

        for label, inputs in (("zip", [full_zip]), ("ics", sorted(raw_dir.glob("*.ics")))):
            out_zip = t / f"trim_{label}.zip"
            res = json.loads(run(["node", HARNESS, HTML, START, END, "-", out_zip, *inputs]))
            check(out_zip.is_file(), f"{label}: zip hasil tidak dibuat")
            with zipfile.ZipFile(out_zip) as z:
                check(z.testzip() is None, f"{label}: zip hasil rusak")
                blob = "\n".join(z.read(n).decode() for n in z.namelist())
                names = z.namelist()
            check(SECRET not in blob, f"{label}: deskripsi/alarm masih ada")
            check("ana@example.test" not in blob, f"{label}: peserta lain masih ada")
            check("LOCATION" not in blob, f"{label}: lokasi masih ada")
            check(OWNER in blob, f"{label}: status pemilik hilang")
            check(res["ukuran"] < full_bytes * 0.15, f"{label}: ukuran tidak mengecil ({res['ukuran']} vs {full_bytes})")
            check(len(names) == 3, f"{label}: jumlah kalender hasil salah: {names}")
            trimmed = ics_json([out_zip], t / f"trim_{label}.json")
            a, b = norm(base), norm(trimmed)
            for k in a:
                check(a[k] == b[k], f"{label}: hasil beda pada '{k}'\nPENUH: {json.dumps(a[k], ensure_ascii=False)[:600]}\nPOTONG: {json.dumps(b[k], ensure_ascii=False)[:600]}")
            print(f"  {label}: {len(base['kandidat'])} kandidat identik; {full_bytes} -> {res['ukuran']} byte")

        # rentang tanpa agenda harus gagal dengan pesan jelas
        r = subprocess.run(["node", HARNESS, HTML, "2017-01-01", "2017-01-31", "-", t / "x.zip", full_zip],
                           capture_output=True, text=True)
        check(r.returncode != 0 and "Tidak ada agenda" in (r.stderr + r.stdout), "rentang kosong tidak ditolak dengan jelas")
    print("OK")


if __name__ == "__main__":
    main()
