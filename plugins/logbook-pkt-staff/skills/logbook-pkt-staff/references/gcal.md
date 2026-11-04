# Sumber: Google Calendar tersambung (hanya bila staf menulis "akses kalender saya" / "pakai gcal")

1. Pastikan tool Google Calendar tersedia. Jika tidak: katakan belum tersambung (sambungkan lewat pengaturan connector) dan tawarkan zip/screenshot. Berhenti.
2. Sebutkan email kalender utama yang tersambung dan minta konfirmasi bahwa itu kalender staf sendiri. Jika akun Claude ini dipakai bersama, kalender yang tersambung milik akun bersama: jangan dilanjutkan, minta zip/screenshot.
3. Ambil agenda **hanya** untuk rentang tanggal yang diminta, jadwal berulang sudah diperluas per kejadian. Ikutkan kalender libur ("Holidays in Indonesia") bila ada. Jika ada beberapa kalender kerja, gunakan semuanya kecuali staf menyebut `kalender: <nama>`.
4. Tulis `gcal_events.json` di folder kerja, hanya field berikut (tanpa deskripsi, lokasi, peserta):
```json
{"pemilik": "<email kalender>",
 "events": [{"kalender": "Kerja", "judul": "Rapat mingguan",
             "mulai": "2026-11-03T09:00:00+07:00", "selesai": "2026-11-03T10:00:00+07:00",
             "respon": "declined|tentative|accepted", "status": "cancelled|tentative|confirmed"}]}
```
   Acara seharian: `mulai`/`selesai` berupa tanggal saja (`2026-11-05`; `selesai` eksklusif).
5. Jalankan `logbook_cepat.py` seperti di SKILL.md dengan `--gcal-json gcal_events.json` sebagai pengganti `--ics`.
