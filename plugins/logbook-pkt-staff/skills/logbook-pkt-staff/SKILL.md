---
name: logbook-pkt-staff
description: Susun logbook harian staf PKT UGM (.xlsx) dari file kalender ICS untuk rentang tanggal tertentu, lengkap dengan blok merah libur, kuning cuti, TTD per hari, dan laporan agenda yang masuk/tidak masuk. Pakai saat staf meminta "logbook PKT", "isi logbook", atau "/logbook-pkt-staff". TTD dan ICS dipakai sekali lalu dihapus.
argument-hint: Nama Lengkap; rentang tanggal (mis. 1 Nov 2026 - 30 Nov 2026) + lampiran TTD dan ICS
---

# Logbook PKT (versi staf)

Panggilan: `/logbook-pkt-staff Nama Lengkap; 1 Nov 2026 - 30 Nov 2026` dengan lampiran **gambar TTD** dan **file .ics**.
Gaya respons: ringkas dan langsung. Bahasa Indonesia.

## Aturan privasi (berlaku sepanjang proses)
- Akun ini dipakai bersama. **Jangan memakai connector** kalender, Gmail, atau Drive, walaupun tersambung. Sumber agenda hanya ICS, screenshot, atau isian staf.
- **Jangan menyimpan** nama, TTD, agenda, atau isi logbook ke memory, Drive, Gmail, maupun berkas di luar folder kerja. Jangan memanggil tool memory.
- Jika chat ini bukan Incognito, sampaikan sekali di awal: "Disarankan memakai Incognito chat. Hapus chat setelah mengunduh file."
- TTD hanya dipakai untuk satu logbook ini. Jangan menampilkan atau mendeskripsikan isi gambar TTD.

## File (relatif terhadap folder skill ini)
- `templates/kosong.xlsx`: basis output. Jangan diubah.
- `scripts/ics_events.py`: ICS -> `events.json` (kandidat, dikecualikan, alasan).
- `scripts/build.py`: agenda JSON + TTD -> xlsx + laporan + hapus TTD/ICS.
- `scripts/selftest.py`: uji dengan data fiktif (hanya untuk pemeliharaan).

## Alur

### 1. Cek masukan (satu pesan, hanya yang kurang)
Perlu: nama lengkap, tanggal mulai dan selesai, gambar TTD, minimal satu file `.ics`.
- Ambil nama dan tanggal dari argumen (dipisah `;`). Ubah tanggal ke format `YYYY-MM-DD`.
- Staf boleh melampirkan beberapa `.ics` (mis. kalender pribadi dan kalender kerja). Jika email kalender tidak terbaca otomatis, tanyakan email kalendernya untuk mendeteksi agenda yang ditolak (opsional).
- Jika ICS belum ada: jelaskan singkat cara ekspor ICS (Google Calendar: Setelan > Impor & ekspor > Ekspor, ekstrak zip, lampirkan file .ics), atau terima screenshot kalender / daftar kegiatan yang diketik staf. Jangan berhenti.
- Jika TTD belum ada: minta dilampirkan. Jangan membuat logbook tanpa TTD kecuali staf menyatakan akan menandatangani manual (pakai gambar kosong putih).

### 2. Libur nasional dan cuti bersama
- Cari SKB 3 Menteri tentang Hari Libur Nasional dan Cuti Bersama tahun terkait (web). Jangan menebak dari ingatan. Jika tidak bisa diakses, tanyakan tanggalnya ke staf.
- `libur_kandidat_dari_ics` hanyalah petunjuk. Kalender libur Google memuat hari peringatan yang bukan libur. Cocokkan dengan SKB sebelum dipakai.
- Libur nasional dan cuti bersama diblok MERAH.

### 3. Baca ICS
```bash
pip install -q -r <folder-skill>/scripts/requirements.txt   # jika belum ada
python <folder-skill>/scripts/ics_events.py --start <mulai> --end <selesai> --ics <file1.ics> [file2.ics ...] [--email <email-kalender>] --out events.json
```
`events.json` berisi: `kandidat` (dengan `id` dan `catatan`), `dikecualikan` (dengan `alasan`: ditolak, dibatalkan, acara sehari penuh), `cuti_pribadi_kandidat`, `libur_kandidat_dari_ics`, `duplikat_digabung`, `di_luar_rentang`, `peringatan_baca`. Semua waktu sudah dalam WIB.

### 4. Cuti pribadi (kuning)
Tampilkan `cuti_pribadi_kandidat` ke staf dan minta konfirmasi dalam satu pertanyaan. Hanya tanggal yang dikonfirmasi yang dimasukkan ke `cuti_pribadi`. Kegiatan di hari cuti tetap ditulis bila ada.

### 5. Ringkas agenda ke bahasa logbook
Dari `kandidat`:
- 1 agenda = 1 butir, kalimat pendek (±5-12 kata), kata kerja di depan: "Rapat ...", "Diskusi ...", "Koordinasi dengan ...", "Menyusun ...", "Review ...".
- Nama proyek atau akronim ditulis apa adanya. Judul berbahasa Inggris boleh dipertahankan.
- Umumnya 3-6 butir per hari, kronologis. Gabungkan agenda yang jelas sama.
- **Jangan mengarang.** Jika judul ambigu ("Meeting", "Call"), tulis apa adanya dan biarkan muncul sebagai peringatan.
- Agenda yang diberi catatan "kemungkinan bukan kegiatan kerja" (makan siang, pengingat, dll.) dibuang, kecuali judulnya jelas kerja. Catat id-nya di `dibuang` dengan alasan singkat.
- Setiap butir harus menyertakan `ids` (id kandidat yang diringkas), agar laporan akurat.
- Tidak boleh ada kandidat yang tidak dipetakan dan tidak dibuang. Jika ragu, tanyakan ke staf.
- Jangan menulis prefiks `> `; skrip menambahkannya.

### 6. Tulis agenda JSON (di folder kerja)
```json
{
  "nama": "Nama Lengkap Staf",
  "kegiatan": {
    "2026-11-02": [
      {"teks": "Rapat koordinasi tim", "ids": [1]},
      {"teks": "Diskusi proposal dengan mitra", "ids": [2, 3]}
    ]
  },
  "dibuang": {"4": "makan siang"},
  "libur": {"2026-11-12": "Nama hari libur"},
  "cuti_bersama": {},
  "cuti_pribadi": ["2026-11-05"]
}
```
Hari kerja tanpa agenda tidak dimasukkan (baris dibiarkan kosong untuk diisi manual).

### 7. Bangun xlsx dan hapus berkas sensitif
```bash
python <folder-skill>/scripts/build.py --start <mulai> --end <selesai> --agenda agenda.json \
  --ttd <file-ttd> --events events.json --hapus <file1.ics> [file2.ics ...] --out <folder-output>
```
Skrip mengisi template (merah untuk akhir pekan/libur tanpa TTD, kuning untuk cuti dengan TTD, TTD di hari kerja), menambah baris bila rentang > 26 hari, membuat laporan JSON, lalu **menghapus TTD dan ICS** dari workspace. Nama berkas: `Logbook_<Nama>_<Periode>.xlsx`.
Jika `gagal_dihapus` tidak kosong, sebutkan berkas mana.
Serahkan file ke staf agar bisa diunduh (folder output / tool pengiriman berkas yang tersedia).

### 8. Laporan (wajib, ringkas)
Sajikan dari output `build.py`:
1. **Masuk**: jumlah butir, jumlah hari kerja terisi, perkiraan total hari kerja (`hari_kerja_perkiraan`; kolom "Total hari kerja" di berkas tetap `...` untuk diisi manual).
2. **Tidak masuk** (tabel: tanggal, jam, judul, alasan): dari `tidak_masuk`.
3. **Peringatan** (tabel dari `peringatan`): bentrok, tentatif, di luar jam kerja, judul ambigu, jatuh di hari libur/cuti. Ditambah `hari_kerja_kosong`, `belum_terpetakan_periksa`, `agenda_di_luar_rentang`, `peringatan_baca_ics`, dan `duplikat_digabung` bila ada.
4. **Merah/kuning**: libur beserta namanya dan tanggal cuti.
5. Penutup, selalu: "TTD dan ICS sudah dihapus dari workspace. Salinan lampiran masih ada di chat ini sampai chat dihapus. Unduh file, periksa laporan di atas, lalu hapus chat ini."

Jika staf meminta revisi setelah build, TTD perlu dilampirkan ulang (sudah dihapus). Pakai kembali `agenda.json` dan `events.json` di folder kerja bila masih ada.

## Uji
`python scripts/selftest.py` memakai data fiktif dan harus mencetak `OK`.
