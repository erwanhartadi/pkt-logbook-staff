---
name: logbook-pkt-staff
description: Susun logbook harian staf PKT UGM (.xlsx) dari zip/.ics kalender, Google Calendar, atau screenshot mingguan, lengkap dengan blok merah libur, kuning cuti, TTD per hari, dan laporan ringkas agenda yang masuk/tidak masuk. Mode hemat token. Pakai saat staf meminta "logbook PKT", "isi logbook", atau "/logbook-pkt-staff".
argument-hint: Nama Lengkap; rentang tanggal (lampirkan TTD dan zip/.ics atau screenshot)
---

# Logbook PKT (staf), mode hemat

Prinsip: pakai kuota seminimal mungkin. Tanpa narasi di antara langkah, tanpa merangkum ulang, maksimal satu pertanyaan (hanya bila masukan wajib kurang). Balasan akhir = berkas + teks laporan dari skrip apa adanya. Bahasa Indonesia.

## 0. Cek kemampuan (satu perintah)
Jalankan `python3 -c "import openpyxl, PIL, dateutil"`.
- Tidak bisa menjalankan kode, atau tidak bisa membuat/mengirim berkas (mis. chat Incognito, atau Code execution dimatikan): balas dua kalimat berisi sebab dan perbaikannya (pakai chat biasa, bukan Incognito; aktifkan *Code execution and file creation* di Settings > Capabilities), lalu **berhenti**. Jangan menulis logbook sebagai teks.
- Modul belum ada: `pip install -q -r <folder-skill>/scripts/requirements.txt`.

## 1. Masukan
Perlu: nama lengkap, tanggal mulai-selesai (ubah ke `YYYY-MM-DD`), gambar TTD, dan satu sumber agenda: **zip/.ics** (default), "akses kalender saya" (Google Calendar), atau **screenshot** mingguan.
Opsi yang boleh ditulis staf di perintah: `kalender: <nama>` (batasi kalender), `libur: <tanggal>` (tanggal libur/cuti bersama), `cuti: <tanggal>`, `rapikan` (mode rapi, lebih boros).
Ada yang kurang: tanyakan sekaligus dalam satu pesan singkat. TTD = gambar berisi tanda tangan (cari di `/mnt/user-data/uploads`); tanya hanya bila benar-benar tidak jelas. Jangan mendeskripsikan isi TTD.

## 2. Jalankan (zip/.ics, paling hemat)
```bash
python <folder-skill>/scripts/logbook_cepat.py --nama "<Nama>" --start <mulai> --end <selesai> \
  --ttd <file-ttd> --ics <zip atau .ics ...> --out <folder-output> \
  [--pakai <nama kalender>] [--libur YYYY-MM-DD=Nama ...] [--cuti YYYY-MM-DD ...]
```
Satu perintah ini membaca kalender (zip berisi banyak .ics boleh, diabaikan yang di luar rentang), memakai judul agenda apa adanya, mengisi template, menghapus TTD dan kalender dari ruang kerja, lalu mencetak `BERKAS: <path>` dan laporan ringkas.
Sumber lain: Google Calendar baca `references/gcal.md`; screenshot baca `references/screenshot.md`. Keduanya menghasilkan `gcal_events.json`, lalu perintah yang sama dengan `--gcal-json` sebagai pengganti `--ics`.

## 3. Serahkan
Kirim berkas dari baris `BERKAS:` ke staf, lalu tempel teks laporan **apa adanya** tanpa tambahan. Staf `rapikan`: ikuti `references/rapi.md`.
Revisi: TTD sudah dihapus, jadi sarankan edit manual di Excel (lebih hemat kuota). Jika staf tetap meminta, minta TTD dilampirkan ulang.

## Privasi
- Jangan memakai connector Gmail atau Drive. Connector Google Calendar hanya bila staf menulis eksplisit "akses kalender saya" (lihat `references/gcal.md`).
- Jangan memanggil tool memory dan jangan menyimpan nama, TTD, atau agenda di luar folder kerja.
- File `.ics` mentah yang dilampirkan langsung bisa membanjiri chat; sarankan zip. Jika isinya sempat tampil di percakapan, tetap proses lewat skrip.
