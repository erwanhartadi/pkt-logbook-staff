# Sumber: screenshot kalender mingguan (4-6 gambar untuk 4 minggu)

Ini jalur paling boros token dan paling rentan salah. Tawarkan zip/.ics lebih dulu bila staf belum mencoba.

1. Minta staf: tampilan **Week**, satu screenshot per minggu, **seluruh jam 00:00-24:00 terlihat** (zoom out browser atau dua screenshot pagi/sore), header tanggal dan label bulan terlihat, hanya kalender kerja dicentang. Judul sering terpotong: sarankan tampilan **Schedule**.
2. Baca tiap gambar: tanggal kolom dari header (perhatikan pergantian bulan/tahun), lalu catat tiap agenda: judul persis seperti tampil, jam mulai-selesai, acara seharian dari baris atas. Zona waktu mengikuti label kiri atas (GMT+7 = +07:00). Acara seharian dari kalender libur (warna/nama "Holidays in Indonesia") dicatat dengan `kalender: "Holidays in Indonesia"`.
3. **Jangan menebak.** Judul terpotong atau jam tidak jelas: isi `ragu` pada agenda itu dengan alasan singkat.
4. Tulis `gcal_events.json` dengan skema di `gcal.md` (`kalender`: "Screenshot" untuk agenda biasa; `pemilik` boleh kosong) ditambah `"tercakup": [["2026-07-26", "2026-08-01"], ...]` berisi rentang tanggal tiap gambar.
5. Jalankan `logbook_cepat.py` dengan `--gcal-json gcal_events.json`. Laporan menyebut tanggal yang belum tercakup; sampaikan apa adanya.
6. Keterbatasan (cukup satu kalimat di balasan bila relevan): agenda yang ditolak biasanya tidak tampil dan tidak bisa dicek.
