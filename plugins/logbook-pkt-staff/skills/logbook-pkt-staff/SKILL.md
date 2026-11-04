---
name: logbook-pkt-staff
description: Susun logbook harian staf PKT UGM (.xlsx) dari screenshot kalender atau akses Google Calendar, lengkap dengan blok merah libur, kuning cuti, TTD per hari, dan laporan ringkas. Mode hemat token. Pakai saat staf menulis "/logbook-pkt-staff", "logbook PKT", atau "isi logbook".
argument-hint: "Nama Lengkap" "rentang tanggal" + lampiran TTD + screenshot kalender (atau tulis: akses kalender saya)
---

# Logbook PKT (staf), mode hemat

Hemat kuota: tanpa narasi di antara langkah, tanpa merangkum ulang, maksimal satu pertanyaan singkat. Balasan akhir = berkas + laporan dari skrip apa adanya. Bahasa Indonesia.

## Format perintah
`/logbook-pkt-staff "Nama Lengkap" "rentang tanggal"` + lampiran **TTD** (gambar tanda tangan), lalu salah satu:
- **Opsi 1**: lampiran **screenshot kalender** (4-6 gambar tampilan Week).
- **Opsi 2**: tulis **akses kalender saya**, Claude membaca Google Calendar yang tersambung.
Pemisah nama dan tanggal boleh tanda kutip atau titik koma. Ubah tanggal ke `YYYY-MM-DD`. Opsi tambahan (boleh): `libur: <tanggal>`, `cuti: <tanggal>`, `kalender: <nama>`, `rapikan`.
Bila nama, tanggal, TTD, atau sumber agenda kurang: tanyakan sekaligus dalam satu pesan pendek (sumber: "kirim screenshot kalender, atau tulis: akses kalender saya"). TTD = gambar bukan-kalender berisi tanda tangan (biasanya bernama ttd); jangan mendeskripsikan isinya, tanya hanya bila tak bisa dibedakan dari screenshot.

## 0. Cek kemampuan
Jalankan `python3 -c "import openpyxl, PIL, dateutil"`. Tidak bisa menjalankan kode atau membuat berkas (mis. chat Incognito, atau Code execution mati): balas dua kalimat (pakai chat biasa, bukan Incognito; aktifkan *Code execution and file creation* di Settings > Capabilities) lalu **berhenti**. Jangan menulis logbook sebagai teks. Modul belum ada: `pip install -q -r <folder-skill>/scripts/requirements.txt`.

## Opsi 1: screenshot
1. Baca tiap gambar kalender. Tanggal kolom dari header (awas pergantian bulan/tahun). Catat tiap agenda: judul persis seperti tampil, mulai-selesai (zona dari label kiri atas; GMT+7 = +07:00), acara seharian dari baris atas. Acara dari kalender libur ("Holidays in Indonesia") dicatat dengan `kalender: "Holidays in Indonesia"`.
2. **Jangan menebak.** Judul terpotong atau jam tidak jelas: isi `ragu` dengan alasan singkat. Jam di luar area terlihat tidak diketahui; jangan dikarang.
3. Tulis `gcal_events.json`:
```json
{"pemilik": "", "events": [{"kalender": "Screenshot", "judul": "Rapat mingguan",
  "mulai": "2026-11-03T09:00:00+07:00", "selesai": "2026-11-03T10:00:00+07:00", "ragu": ""}],
 "tercakup": [["2026-11-02", "2026-11-08"], ["2026-11-09", "2026-11-15"]]}
```
Acara seharian: `mulai`/`selesai` berupa tanggal saja (`selesai` eksklusif). `tercakup` = rentang tanggal tiap gambar.

## Opsi 2: Google Calendar
1. Tool Google Calendar tidak ada: katakan belum tersambung (Settings > Connectors) dan tawarkan screenshot. Berhenti.
2. Sebutkan email kalender yang tersambung, minta konfirmasi bahwa itu milik staf sendiri. Akun Claude dipakai bersama (kantor): jangan lanjut, minta screenshot.
3. Ambil agenda **hanya** pada rentang tanggal, jadwal berulang diperluas, termasuk kalender libur bila ada. Beberapa kalender kerja: pakai semuanya kecuali ada `kalender:`.
4. Tulis `gcal_events.json` skema sama seperti di atas (tanpa `tercakup`; `pemilik` = email kalender; tambah `"respon": "declined|tentative|accepted"` dan `"status": "cancelled|tentative|confirmed"` bila diketahui). Tanpa deskripsi, lokasi, atau peserta.

## Jalankan (satu perintah)
```bash
python <folder-skill>/scripts/logbook_cepat.py --nama "<Nama>" --start <mulai> --end <selesai> \
  --ttd <file-ttd> --gcal-json gcal_events.json --hapus-juga <semua screenshot> \
  --out <folder-output> [--libur YYYY-MM-DD=Nama ...] [--cuti YYYY-MM-DD ...] [--pakai <kalender>]
```
Skrip memakai judul agenda apa adanya, membuang agenda non-kerja/ditolak/kembar (tetap dilaporkan), mengisi template, menghapus TTD, JSON, dan screenshot dari ruang kerja, lalu mencetak `BERKAS: <path>` dan laporan ringkas.

## Serahkan
Kirim berkas dari baris `BERKAS:`, lalu tempel laporan **apa adanya** tanpa tambahan. Staf `rapikan`: ikuti `references/rapi.md`. Revisi: sarankan edit manual di Excel (TTD sudah dihapus; revisi lewat chat butuh TTD dilampirkan ulang).
Cadangan tak diiklankan: bila staf melampirkan zip/.ics ekspor kalender, ganti `--gcal-json ...` dengan `--ics <zip>` (zip jangan diekstrak).

## Privasi
- Jangan memakai connector Gmail atau Drive. Google Calendar hanya bila staf menulis "akses kalender saya".
- Jangan memanggil tool memory; jangan menyimpan nama, TTD, atau agenda di luar folder kerja.
