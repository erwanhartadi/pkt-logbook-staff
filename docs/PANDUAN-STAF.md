# Panduan: Menyusun Logbook PKT dengan Claude (1 halaman)

## Sebelum mulai
1. Buka Claude kantor dan mulai **Incognito chat** (ikon hantu di pojok atas). Chat tidak masuk riwayat atau memori.
2. Siapkan dua berkas:
   - **Tanda tangan**: foto atau scan di atas kertas putih (PNG/JPG).
   - **Kalender**: file .zip/.ics hasil ekspor, lihat langkah di bawah.

## Ekspor kalender (Google Calendar, lewat komputer)
1. Buka calendar.google.com, klik ikon roda gigi > **Setelan**.
2. Pilih **Impor & ekspor** > **Ekspor**. File **.zip** terunduh.
3. Ini normal: isinya **semua kalender dan seluruh riwayat** Anda, dan tidak bisa dibatasi rentang tanggal. **Tidak perlu diekstrak atau dipotong**, lampirkan zip-nya. Claude hanya mengambil agenda pada rentang yang Anda minta, dan akan bertanya kalender mana yang dipakai (biasanya kalender kerja).

Tidak nyaman mengunggah seluruh kalender? Pilihan lain:
- Ekspor satu kalender saja: Setelan > klik nama kalender di kiri > **Ekspor kalender** (tetap seluruh riwayat kalender itu).
- Kirim screenshot kalender untuk rentang yang diminta, atau ketik daftar kegiatan per tanggal.

## Meminta logbook
Ketik di chat dan lampirkan TTD serta file `.ics`:

`/logbook-pkt-staff Nama Lengkap Anda; 1 November 2026 - 30 November 2026`

Claude mungkin bertanya: tanggal cuti Anda (konfirmasi), email kalender, atau agenda yang judulnya tidak jelas.

## Membaca hasil
Anda akan menerima:
- **File logbook (.xlsx)**: merah = akhir pekan/libur (tanpa TTD), kuning = cuti.
- **Laporan**:
  - *Masuk*: jumlah kegiatan yang ditulis.
  - *Tidak masuk*: agenda yang ditolak, dibatalkan, acara seharian, atau bukan kegiatan kerja, beserta alasannya.
  - *Peringatan*: agenda bentrok, tentatif, di luar jam kerja, judul tidak jelas, atau jatuh di hari libur. Hari kerja tanpa kegiatan juga dicantumkan.

Periksa laporan. Isi manual hari yang kosong dan kolom "Total hari kerja".

## Setelah selesai (wajib)
1. **Unduh** file logbook.
2. **Hapus chat** ini (menu chat > Hapus). TTD dan ICS sudah dihapus dari ruang kerja Claude, tetapi lampiran masih tersimpan di chat sampai chat dihapus.
3. Jangan menyimpan TTD atau kalender ke Drive bersama akun ini.

## Catatan
- Akun ini dipakai bersama. Jangan menyambungkan kalender, Gmail, atau Drive pribadi ke akun ini.
- Kalau hasil belum sesuai, minta revisi di chat yang sama sebelum menghapusnya. TTD perlu dilampirkan ulang.
