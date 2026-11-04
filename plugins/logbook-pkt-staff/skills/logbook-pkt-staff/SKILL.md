---
name: logbook-pkt-staff
description: Susun logbook harian staf PKT UGM (.xlsx) dari file kalender ICS (atau Google Calendar bila staf memintanya) untuk rentang tanggal tertentu, lengkap dengan blok merah libur, kuning cuti, TTD per hari, dan laporan agenda yang masuk/tidak masuk. Pakai saat staf meminta "logbook PKT", "isi logbook", atau "/logbook-pkt-staff". TTD dan ICS dipakai sekali lalu dihapus.
argument-hint: Nama Lengkap; rentang tanggal (mis. 1 Nov 2026 - 30 Nov 2026) + lampiran TTD dan ICS
---

# Logbook PKT (versi staf)

Panggilan: `/logbook-pkt-staff Nama Lengkap; 1 Nov 2026 - 30 Nov 2026` dengan lampiran **gambar TTD** dan **file .ics**.
Gaya respons: ringkas dan langsung. Bahasa Indonesia.

## Aturan privasi (berlaku sepanjang proses)
- Akun bisa dipakai bersama. **Jangan memakai connector Gmail atau Drive.** Connector Google Calendar **hanya** dipakai bila staf menulis eksplisit di chat (mis. "akses kalender saya", "pakai gcal"); lihat langkah 3b. Selain itu sumber agenda adalah ICS, screenshot, atau isian staf.
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
Perlu: nama lengkap, tanggal mulai dan selesai, gambar TTD, minimal satu file `.ics` atau `.zip` hasil ekspor kalender, atau permintaan eksplisit "akses kalender saya" (Google Calendar, lihat 3b), atau 4-6 screenshot kalender mingguan (lihat 3c). Jika ada beberapa gambar dan tidak jelas mana TTD-nya, tanyakan.
- Ambil nama dan tanggal dari argumen (dipisah `;`). Ubah tanggal ke format `YYYY-MM-DD`.
- Ekspor Google Calendar selalu berisi **semua kalender dan seluruh riwayat** (file `.zip` berisi banyak `.ics`) dan tidak bisa dibatasi rentang tanggal. Itu tidak masalah: skrip hanya mengambil agenda di dalam rentang. Terima `.zip` apa adanya; jangan minta staf mengekstrak atau memotongnya. Beberapa `.ics` terpisah juga boleh.
- `.ics` mentah yang dilampirkan langsung berupa teks dan bisa membanjiri chat (galat "exceeds context limit") atau terbaca sebagian. Jika staf mengalaminya, sarankan melampirkan sebagai `.zip` (kompres file `.ics`, atau pakai Pemotong Kalender di repo). Jika isi `.ics` sempat tampil di percakapan, tetap proses lewat skrip dari berkas; jangan meringkas dari teks yang tampak.
- Jika email kalender tidak terbaca otomatis, tanyakan email kalendernya untuk mendeteksi agenda yang ditolak (opsional).
- Jika ICS belum ada: jelaskan singkat cara ekspor ICS (Google Calendar: Setelan > Impor & ekspor > Ekspor, ekstrak zip, lampirkan file .ics), atau terima screenshot kalender / daftar kegiatan yang diketik staf. Jangan berhenti.
- Jika TTD belum ada: minta dilampirkan. Jangan membuat logbook tanpa TTD kecuali staf menyatakan akan menandatangani manual (pakai gambar kosong putih).

### 2. Libur nasional dan cuti bersama
- Cari SKB 3 Menteri tentang Hari Libur Nasional dan Cuti Bersama tahun terkait (web). Jangan menebak dari ingatan. Jika tidak bisa diakses, tanyakan tanggalnya ke staf.
- `libur_kandidat_dari_ics` hanyalah petunjuk. Kalender libur Google memuat hari peringatan yang bukan libur. Cocokkan dengan SKB sebelum dipakai.
- Libur nasional dan cuti bersama diblok MERAH.

### 3. Baca ICS
```bash
pip install -q -r <folder-skill>/scripts/requirements.txt   # jika belum ada
python <folder-skill>/scripts/ics_events.py --start <mulai> --end <selesai> --ics <file.zip | file1.ics ...> [--email <email-kalender>] [--pakai <teks nama kalender> ...] --out events.json
```
`events.json` berisi: `kandidat` (dengan `id` dan `catatan`), `dikecualikan` (dengan `alasan`: ditolak, dibatalkan, acara sehari penuh), `cuti_pribadi_kandidat`, `libur_kandidat_dari_ics`, `duplikat_digabung`, `di_luar_rentang`, `peringatan_baca`. Semua waktu sudah dalam WIB.

Periksa `kalender` di output (tiap kalender beserta `agenda_di_rentang`). Jika lebih dari satu kalender punya agenda, tanyakan ke staf dalam satu pertanyaan kalender mana yang dipakai untuk logbook (biasanya kalender kerja; kalender pribadi, ulang tahun, atau hari libur biasanya tidak), lalu jalankan ulang dengan `--pakai <potongan nama kalender atau berkas>`. Jangan menampilkan judul agenda dari kalender yang tidak dipilih atau dari luar rentang.

### 3b. Alternatif: Google Calendar (hanya jika staf menulis "akses kalender saya" / "pakai gcal")
1. Pastikan tool Google Calendar tersedia. Jika tidak, katakan belum tersambung (sambungkan lewat pengaturan connector) dan tawarkan ICS.
2. Sebutkan akun kalender yang tersambung (email kalender utama) dan minta konfirmasi bahwa itu kalender staf sendiri. Jika akun Claude ini dipakai bersama, kalender yang tersambung milik akun bersama, bukan milik staf: jangan dilanjutkan, minta ICS.
3. Ambil agenda **hanya** untuk rentang tanggal yang diminta, dengan jadwal berulang sudah diperluas per kejadian. Jika ada beberapa kalender, tanyakan kalender mana yang dipakai (satu pertanyaan).
4. Tulis `gcal_events.json` di folder kerja dengan field minimal berikut. Jangan menyimpan deskripsi, lokasi, atau peserta.
```json
{"pemilik": "<email kalender>",
 "events": [{"kalender": "Kerja", "judul": "Rapat mingguan",
             "mulai": "2026-11-03T09:00:00+07:00", "selesai": "2026-11-03T10:00:00+07:00",
             "respon": "declined|tentative|accepted", "status": "cancelled|tentative|confirmed"}]}
```
   Acara seharian: `mulai`/`selesai` berupa tanggal saja (`2026-11-05`; `selesai` eksklusif). `respon` adalah tanggapan staf terhadap undangan.
5. Jalankan `python <folder-skill>/scripts/ics_events.py --gcal-json gcal_events.json --start <mulai> --end <selesai> --out events.json` (tanpa `--ics`), lalu lanjut ke langkah 4 seperti biasa. Tambahkan `gcal_events.json` ke `--hapus` di langkah 7.
6. Ingatkan: hasil bacaan kalender tetap tampil di chat sampai chat dihapus.

### 3c. Alternatif: screenshot kalender mingguan
Untuk staf yang tidak mengekspor dan tidak menyambungkan kalender. Rentang 4 minggu biasanya 4-6 gambar.
1. Minta staf mengambilnya begini: tampilan **Week** di Google Calendar, satu screenshot per minggu; **seluruh jam 00:00-24:00 harus terlihat** (zoom out browser dengan Ctrl/Cmd minus, atau dua screenshot pagi/sore per minggu); header tanggal dan label bulan ikut terlihat; hanya kalender kerja yang dicentang. Jika judul sering terpotong, tampilan **Schedule** lebih akurat.
2. Baca tiap gambar: tentukan tanggal kolom dari header (perhatikan pergantian bulan/tahun dari label bulan), lalu transkripsikan setiap agenda: judul persis seperti tampil, jam mulai-selesai (dari label jam pada blok atau posisinya terhadap sumbu jam), dan acara seharian dari baris atas. Zona waktu: ikuti label di kiri atas (mis. GMT+7 = +07:00).
3. **Jangan menebak.** Judul terpotong, jam tidak jelas, atau blok yang tumpang tindih sempit: isi `ragu` pada agenda itu dengan alasan singkat.
4. Tulis `gcal_events.json` dengan skema 3b (`kalender`: "Screenshot", `pemilik` boleh dikosongkan), ditambah `"tercakup": [["2026-07-26", "2026-08-01"], ...]` berisi rentang tanggal tiap gambar. Jalankan seperti 3b langkah 5.
5. Laporan memuat `tanggal_tidak_tercakup`: minta screenshot tambahan untuk tanggal itu sebelum melanjutkan bila ada hari kerja yang terlewat.
6. Sampaikan keterbatasannya ke staf: agenda yang ditolak biasanya disembunyikan Google Calendar sehingga tidak terlihat dan tidak bisa dicek; agenda di luar jam yang terlihat hilang; akurasi bergantung keterbacaan gambar, jadi periksa butir bertanda "periksa".

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
  --ttd <file-ttd> --events events.json --hapus <file.zip | file1.ics | gcal_events.json ...> --out <folder-output>
```
Skrip mengisi template (merah untuk akhir pekan/libur tanpa TTD, kuning untuk cuti dengan TTD, TTD di hari kerja), menambah baris bila rentang > 26 hari, membuat laporan JSON, lalu **menghapus TTD dan ICS** dari workspace. Nama berkas: `Logbook_<Nama>_<Periode>.xlsx`.
Jika `gagal_dihapus` tidak kosong, sebutkan berkas mana.
Serahkan file ke staf agar bisa diunduh (folder output / tool pengiriman berkas yang tersedia).

### 8. Laporan (wajib, ringkas)
Sajikan dari output `build.py`:
1. **Masuk**: jumlah butir, jumlah hari kerja terisi, perkiraan total hari kerja (`hari_kerja_perkiraan`; kolom "Total hari kerja" di berkas tetap `...` untuk diisi manual).
2. **Tidak masuk** (tabel: tanggal, jam, judul, alasan): dari `tidak_masuk`.
3. **Peringatan** (tabel dari `peringatan`): bentrok, tentatif, di luar jam kerja, judul ambigu, jatuh di hari libur/cuti. Ditambah `tanggal_tidak_tercakup` (jalur screenshot), `hari_kerja_kosong`, `belum_terpetakan_periksa`, `agenda_di_luar_rentang`, `peringatan_baca_ics`, dan `duplikat_digabung` bila ada.
4. **Merah/kuning**: libur beserta namanya dan tanggal cuti.
5. Penutup, selalu: "TTD dan ICS sudah dihapus dari workspace. Salinan lampiran masih ada di chat ini sampai chat dihapus. Unduh file, periksa laporan di atas, lalu hapus chat ini."

Jika staf meminta revisi setelah build, TTD perlu dilampirkan ulang (sudah dihapus). Pakai kembali `agenda.json` dan `events.json` di folder kerja bila masih ada.

## Uji
`python scripts/selftest.py` memakai data fiktif dan harus mencetak `OK`.
