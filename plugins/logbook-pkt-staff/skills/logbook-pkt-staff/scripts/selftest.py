#!/usr/bin/env python3
"""Uji ujung ke ujung dengan data FIKTIF (tanpa data pribadi siapa pun).

Membuat ICS sintetis + TTD dummy, menjalankan ics_events.py dan build.py,
lalu memeriksa hasil. Cetak 'OK' bila semua lolos.
"""
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from openpyxl import load_workbook
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
OWNER = "staf.contoh@example.test"

MAIN_ICS = f"""BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:{OWNER}
BEGIN:VEVENT
UID:e1
SUMMARY:Rapat koordinasi tim
DTSTART;TZID=Asia/Jakarta:20261102T090000
DTEND;TZID=Asia/Jakarta:20261102T100000
END:VEVENT
BEGIN:VEVENT
UID:e2
SUMMARY:Diskusi proposal
DTSTART;TZID=Asia/Jakarta:20261102T093000
DTEND;TZID=Asia/Jakarta:20261102T103000
END:VEVENT
BEGIN:VEVENT
UID:e3
SUMMARY:Webinar kesehatan
DTSTART:20261103T060000Z
DTEND:20261103T070000Z
END:VEVENT
BEGIN:VEVENT
UID:e4
SUMMARY:Lunch
DTSTART;TZID=Asia/Jakarta:20261103T120000
DTEND;TZID=Asia/Jakarta:20261103T130000
END:VEVENT
BEGIN:VEVENT
UID:e5
SUMMARY:Rapat yang ditolak
DTSTART;TZID=Asia/Jakarta:20261104T100000
DTEND;TZID=Asia/Jakarta:20261104T110000
ATTENDEE;PARTSTAT=DECLINED;CN=Staf Contoh:mailto:{OWNER}
END:VEVENT
BEGIN:VEVENT
UID:e6
SUMMARY:Rapat dibatalkan
STATUS:CANCELLED
DTSTART;TZID=Asia/Jakarta:20261104T130000
DTEND;TZID=Asia/Jakarta:20261104T140000
END:VEVENT
BEGIN:VEVENT
UID:e7
SUMMARY:Cuti tahunan
DTSTART;VALUE=DATE:20261105
DTEND;VALUE=DATE:20261106
END:VEVENT
BEGIN:VEVENT
UID:e8
SUMMARY:Konsultasi daring luar negeri
DTSTART;TZID=America/New_York:20261105T220000
DTEND;TZID=America/New_York:20261105T230000
END:VEVENT
BEGIN:VEVENT
UID:e9
SUMMARY:Weekly sync
DTSTART;TZID=Asia/Jakarta:20261102T080000
DTEND;TZID=Asia/Jakarta:20261102T083000
RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=4
EXDATE;TZID=Asia/Jakarta:20261109T080000
END:VEVENT
BEGIN:VEVENT
UID:e9
SUMMARY:Weekly sync (dipindah)
RECURRENCE-ID;TZID=Asia/Jakarta:20261116T080000
DTSTART;TZID=Asia/Jakarta:20261116T100000
DTEND;TZID=Asia/Jakarta:20261116T103000
END:VEVENT
BEGIN:VEVENT
UID:e10
SUMMARY:Kerja akhir pekan
DTSTART;TZID=Asia/Jakarta:20261107T100000
DTEND;TZID=Asia/Jakarta:20261107T110000
END:VEVENT
BEGIN:VEVENT
UID:e11
SUMMARY:Diskusi tentatif
DTSTART;TZID=Asia/Jakarta:20261109T140000
DTEND;TZID=Asia/Jakarta:20261109T150000
ATTENDEE;PARTSTAT=TENTATIVE;CN=Staf Contoh:mailto:{OWNER}
END:VEVENT
BEGIN:VEVENT
UID:e12
SUMMARY:Pengolahan data malam
DTSTART;TZID=Asia/Jakarta:20261110T230000
DTEND;TZID=Asia/Jakarta:20261110T233000
END:VEVENT
BEGIN:VEVENT
UID:e13
SUMMARY:Meeting
DTSTART;TZID=Asia/Jakarta:20261111T090000
DTEND;TZID=Asia/Jakarta:20261111T100000
END:VEVENT
BEGIN:VEVENT
UID:e14
SUMMARY:Di luar rentang
DTSTART;TZID=Asia/Jakarta:20261130T090000
DTEND;TZID=Asia/Jakarta:20261130T100000
END:VEVENT
END:VCALENDAR
"""

DUP_ICS = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Kalender Tim
BEGIN:VEVENT
UID:dup1
SUMMARY:Rapat koordinasi tim
DTSTART;TZID=Asia/Jakarta:20261102T090000
DTEND;TZID=Asia/Jakarta:20261102T100000
END:VEVENT
END:VCALENDAR
"""

HOLIDAY_ICS = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Holidays in Indonesia
BEGIN:VEVENT
UID:h1
SUMMARY:Hari Contoh Libur
DTSTART;VALUE=DATE:20261112
DTEND;VALUE=DATE:20261113
END:VEVENT
END:VCALENDAR
"""


def run(*args):
    r = subprocess.run([sys.executable, "-I", *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"GAGAL: {args[0]}\n{r.stdout}\n{r.stderr}")
    return json.loads(r.stdout)


def check(cond, msg):
    if not cond:
        sys.exit(f"GAGAL: {msg}")


def test_zip():
    """Ekspor Google Calendar = zip berisi banyak .ics + seluruh riwayat."""
    pribadi = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Pribadi
BEGIN:VEVENT
UID:p1
SUMMARY:Olahraga pagi
DTSTART;TZID=Asia/Jakarta:20200101T060000
DTEND;TZID=Asia/Jakarta:20200101T070000
RRULE:FREQ=DAILY
END:VEVENT
BEGIN:VEVENT
UID:p2
SUMMARY:Acara tahun lalu
DTSTART;TZID=Asia/Jakarta:20231005T090000
DTEND;TZID=Asia/Jakarta:20231005T100000
END:VEVENT
END:VCALENDAR
"""
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        z = t / "calendar-export.zip"
        with zipfile.ZipFile(z, "w") as zf:
            zf.writestr(f"{OWNER}.ics", MAIN_ICS)
            zf.writestr("Pribadi.ics", pribadi)
            zf.writestr("catatan.txt", "bukan kalender")
        out = t / "ev.json"
        res = run(HERE / "ics_events.py", "--start", "2026-11-02", "--end", "2026-11-06", "--ics", z, "--out", out)
        check(len(res["kalender"]) == 2, f"zip: jumlah kalender salah: {res['kalender']}")
        ev = json.loads(out.read_text(encoding="utf-8"))
        check(sum(k["judul"] == "Olahraga pagi" for k in ev["kandidat"]) == 5, "zip: jadwal harian sejak 2020 salah")
        check(not any(k["judul"] == "Acara tahun lalu" for k in ev["kandidat"]), "zip: agenda lama ikut masuk")
        out2 = t / "ev2.json"
        res2 = run(HERE / "ics_events.py", "--start", "2026-11-02", "--end", "2026-11-06", "--ics", z,
                   "--pakai", "staf.contoh", "--out", out2)
        ev2 = json.loads(out2.read_text(encoding="utf-8"))
        check(not any(k["judul"] == "Olahraga pagi" for k in ev2["kandidat"]), "zip: --pakai tidak menyaring kalender")
        check([k["dipakai"] for k in res2["kalender"]].count(False) == 1, "zip: status dipakai salah")


def test_gcal():
    """Jalur Google Calendar: JSON ringkas -> pipeline yang sama."""
    data = {"pemilik": OWNER, "events": [
        {"kalender": "Kerja", "judul": "Rapat mingguan", "mulai": "2026-11-03T09:00:00+07:00", "selesai": "2026-11-03T10:00:00+07:00"},
        {"kalender": "Kerja", "judul": "Webinar UTC", "mulai": "2026-11-03T06:00:00Z", "selesai": "2026-11-03T07:00:00Z"},
        {"kalender": "Kerja", "judul": "Rapat ditolak", "mulai": "2026-11-04T10:00:00+07:00", "selesai": "2026-11-04T11:00:00+07:00", "respon": "declined"},
        {"kalender": "Kerja", "judul": "Rapat batal", "mulai": "2026-11-04T13:00:00+07:00", "selesai": "2026-11-04T14:00:00+07:00", "status": "cancelled"},
        {"kalender": "Kerja", "judul": "Cuti tahunan", "mulai": "2026-11-05", "selesai": "2026-11-06"},
        {"kalender": "Kerja", "judul": "Diskusi tentatif", "mulai": "2026-11-05T14:00:00+07:00", "selesai": "2026-11-05T15:00:00+07:00", "respon": "tentative"},
        {"kalender": "Holidays in Indonesia", "judul": "Hari Contoh Libur", "mulai": "2026-11-12", "selesai": "2026-11-13"},
        {"kalender": "Kerja", "judul": "Di luar rentang", "mulai": "2026-12-01T09:00:00+07:00", "selesai": "2026-12-01T10:00:00+07:00"},
    ]}
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        jp, out = t / "gcal_events.json", t / "ev.json"
        jp.write_text(json.dumps(data), encoding="utf-8")
        res = run(HERE / "ics_events.py", "--start", "2026-11-02", "--end", "2026-11-20", "--gcal-json", jp, "--out", out)
        ev = json.loads(out.read_text(encoding="utf-8"))
        judul = {k["judul"]: k for k in ev["kandidat"]}
        check(len(res["kalender"]) == 2, f"gcal: ringkasan kalender salah: {res['kalender']}")
        check(judul["Webinar UTC"]["mulai"] == "13:00", "gcal: konversi UTC salah")
        check(any(x["alasan"].startswith("ditolak") for x in ev["dikecualikan"]), "gcal: declined tidak dikecualikan")
        check(any(x["alasan"].startswith("dibatalkan") for x in ev["dikecualikan"]), "gcal: cancelled tidak dikecualikan")
        check("2026-11-05" in ev["cuti_pribadi_kandidat"], "gcal: cuti tidak terdeteksi")
        check("tentatif" in judul["Diskusi tentatif"]["catatan"], "gcal: tentatif tidak ditandai")
        check("2026-11-12" in ev["libur_kandidat_dari_ics"], "gcal: libur tidak terdeteksi")
        check(ev["di_luar_rentang"] == 1, f"gcal: di luar rentang salah: {ev['di_luar_rentang']}")


def main():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        ics = [t / "a.ics", t / "b.ics", t / "c.ics"]
        for p, txt in zip(ics, (MAIN_ICS, DUP_ICS, HOLIDAY_ICS)):
            p.write_text(txt, encoding="utf-8")
        ttd = t / "ttd.png"
        im = Image.new("RGB", (300, 200), "white")
        ImageDraw.Draw(im).line([(20, 150), (80, 40), (140, 160), (200, 60), (280, 140)], fill="black", width=5)
        im.save(ttd)

        ev_path = t / "events.json"
        res = run(HERE / "ics_events.py", "--start", "2026-11-02", "--end", "2026-11-20",
                  "--ics", *ics, "--out", ev_path)
        ev = json.loads(ev_path.read_text(encoding="utf-8"))
        judul = {k["judul"]: k for k in ev["kandidat"]}
        check(ev["duplikat_digabung"] == 1, "duplikat tidak digabung")
        check(any(x["alasan"].startswith("ditolak") for x in ev["dikecualikan"]), "declined tidak dikecualikan")
        check(any(x["alasan"].startswith("dibatalkan") for x in ev["dikecualikan"]), "cancelled tidak dikecualikan")
        check("2026-11-05" in ev["cuti_pribadi_kandidat"], "cuti tidak terdeteksi")
        check("2026-11-12" in ev["libur_kandidat_dari_ics"], "libur dari kalender libur tidak terdeteksi")
        check(judul["Konsultasi daring luar negeri"]["tanggal"] == "2026-11-06", "konversi zona waktu salah")
        check(judul["Konsultasi daring luar negeri"]["mulai"] == "10:00", "jam hasil konversi salah")
        check(judul["Webinar kesehatan"]["mulai"] == "13:00", "konversi UTC salah")
        weekly = [k for k in ev["kandidat"] if k["judul"].startswith("Weekly sync")]
        check([k["tanggal"] for k in weekly] == ["2026-11-02", "2026-11-16"], f"RRULE/EXDATE/override salah: {weekly}")
        check(weekly[1]["mulai"] == "10:00", "override tidak dipakai")
        check(ev["di_luar_rentang"] == 1, f"agenda di luar rentang salah hitung: {ev['di_luar_rentang']}")
        check(any("bentrok" in c for c in judul["Rapat koordinasi tim"]["catatan"]), "bentrok tidak terdeteksi")
        check("tentatif" in judul["Diskusi tentatif"]["catatan"], "tentatif tidak ditandai")
        check(any("luar jam" in c for c in judul["Pengolahan data malam"]["catatan"]), "di luar jam tidak ditandai")
        check("judul ambigu" in judul["Meeting"]["catatan"], "judul ambigu tidak ditandai")
        check(any("bukan kegiatan kerja" in c for c in judul["Lunch"]["catatan"]), "lunch tidak ditandai")

        # agenda dummy dari kandidat
        kegiatan, dibuang = {}, {}
        for k in ev["kandidat"]:
            if k["judul"] == "Lunch":
                dibuang[str(k["id"])] = "bukan kegiatan kerja"
            elif k["judul"] == "Meeting":
                pass  # sengaja tidak dipetakan -> harus muncul di 'belum_terpetakan_periksa'
            else:
                kegiatan.setdefault(k["tanggal"], []).append({"teks": k["judul"], "ids": [k["id"]]})
        agenda = {"nama": "Staf Contoh", "kegiatan": kegiatan, "dibuang": dibuang,
                  "libur": {"2026-11-12": "Hari Contoh Libur"}, "cuti_pribadi": ["2026-11-05"]}
        ag_path = t / "agenda.json"
        ag_path.write_text(json.dumps(agenda, ensure_ascii=False), encoding="utf-8")

        out_dir = t / "out"
        rep = run(HERE / "build.py", "--start", "2026-11-02", "--end", "2026-11-20", "--agenda", ag_path,
                  "--ttd", ttd, "--events", ev_path, "--hapus", *ics, "--out", out_dir)
        xlsx = Path(rep["output"])
        check(xlsx.is_file(), "xlsx tidak dibuat")
        check(not ttd.exists(), "TTD tidak dihapus")
        check(all(not p.exists() for p in ics), "ICS tidak dihapus")
        check(not rep["gagal_dihapus"], "ada berkas gagal dihapus")
        check(any(b["judul"] == "Meeting" for b in rep["belum_terpetakan_periksa"]), "agenda belum terpetakan tidak dilaporkan")
        check(any(x["alasan"] == "bukan kegiatan kerja" for x in rep["tidak_masuk"]), "alasan dibuang tidak masuk laporan")
        check(any(p["judul"] == "Diskusi tentatif" for p in rep["peringatan"]), "peringatan tentatif tidak ada di laporan")

        wb = load_workbook(xlsx)
        ws = wb.worksheets[0]
        check(ws["C2"].value == ": Staf Contoh", "nama salah")
        check(ws["C3"].value == ": 2 November - 20 November 2026", f"periode salah: {ws['C3'].value}")
        hari_kerja_bertanda = 0
        for r in range(6, 6 + 19):
            tgl = ws.cell(r, 2).value
            merah = ws.cell(r, 3).fill.fgColor.rgb == "FFFF0000"
            check(merah == (tgl.weekday() >= 5 or tgl.day == 12), f"warna merah salah di {tgl}")
            if not merah:
                hari_kerja_bertanda += 1
        check(ws["C" + str(6 + 3)].fill.fgColor.rgb == "FFFFFF00", "kuning cuti pribadi salah")  # 5 Nov
        check(len(ws._images) == hari_kerja_bertanda, f"jumlah TTD {len(ws._images)} != {hari_kerja_bertanda}")
        check(wb.properties.creator == "Logbook PKT", "metadata creator tidak bersih")
    test_zip()
    test_gcal()
    print("OK")


if __name__ == "__main__":
    main()
