# Panduan: Menyusun Logbook PKT dengan Claude (1 halaman)

## Sebelum mulai
1. Buka **chat baru biasa** di akun Claude pribadi Anda. **Jangan Incognito**: chat Incognito tidak bisa membuat file, sehingga logbook tidak akan jadi. Skill harus sudah terpasang (lihat README) dan *Code execution and file creation* menyala.
2. Siapkan dua berkas:
   - **Tanda tangan**: foto atau scan di atas kertas putih (PNG/JPG).
   - **Kalender**: zip hasil ekspor atau zip dari Pemotong Kalender, lihat langkah di bawah.

## Ekspor kalender (Google Calendar, lewat komputer)
1. Buka calendar.google.com, klik ikon roda gigi > **Setelan**.
2. Pilih **Impor & ekspor** > **Ekspor**. File **.zip** terunduh. Isinya semua kalender dan seluruh riwayat Anda (tidak bisa dibatasi rentang tanggal).

**Jangan melampirkan file `.ics` hasil ekstrak.** File `.ics` berupa teks, sehingga isinya langsung masuk ke chat dan bisa melebihi batas (muncul pesan *"This request exceeds Claude's context limit"*). Dua cara aman:

**Cara A (tercepat): lampirkan zip-nya apa adanya**, tanpa diekstrak. Sudah punya `.ics` saja? Kompres dulu: Mac klik kanan > **Compress**; Windows klik kanan > **Send to** > **Compressed (zipped) folder**.

**Cara B (disarankan, lebih ringan dan privat): Pemotong Kalender.**
1. Unduh `dist/pemotong-kalender.html` dari repo (buka berkasnya di GitHub, klik **Download raw file**), lalu buka dengan klik dua kali di Chrome, Edge, atau Safari terbaru.
2. Pilih zip ekspor, isi rentang tanggal logbook, klik **Potong kalender**.
3. Unduh `kalender-ringkas_...zip` dan lampirkan itu ke Claude.

Pemotong berjalan di browser Anda; kalender tidak diunggah ke mana pun. Hasilnya hanya berisi agenda pada rentang itu (judul dan waktu), tanpa riwayat lama, deskripsi, lokasi, atau peserta lain. Ukurannya biasanya beberapa KB.

Tidak ingin memakai keduanya? Kirim screenshot kalender untuk rentang yang diminta, atau ketik daftar kegiatan per tanggal.

## Alternatif tanpa ekspor: Google Calendar tersambung (akun pribadi)
Jika Google Calendar Anda sudah tersambung ke Claude (menu Connectors/Integrations), Anda bisa melewati ekspor. Tambahkan `akses kalender saya` pada perintah:

`/logbook-pkt-staff Nama Lengkap Anda; 1 November 2026 - 30 November 2026; akses kalender saya`

Claude akan menyebutkan akun kalender yang tersambung dan meminta konfirmasi, lalu hanya membaca rentang tanggal yang diminta. **Jangan memakai cara ini di akun bersama**: kalender yang tersambung milik akun bersama, bukan milik Anda.

## Alternatif tanpa ekspor: screenshot kalender per minggu
Untuk rentang 4 minggu, siapkan 4-6 screenshot:
1. Buka Google Calendar, pilih tampilan **Week**. Centang hanya kalender kerja Anda.
2. Pastikan **seluruh jam 00:00-24:00 terlihat**: perkecil browser dengan Ctrl/Cmd + tanda minus beberapa kali, atau ambil dua screenshot (pagi dan sore) per minggu. Tanggal dan nama bulan di bagian atas harus ikut terlihat.
3. Satu screenshot per minggu. Jika judul sering terpotong, coba tampilan **Schedule** (daftar).
4. Lampirkan semua gambar beserta TTD, lalu ketik perintah seperti biasa.

Keterbatasan: agenda yang Anda tolak biasanya tidak tampil di screenshot dan tidak bisa dicek, dan judul yang terpotong akan ditandai "periksa" di laporan. Claude akan memberi tahu jika ada tanggal yang belum tercakup.

## Meminta logbook
Ketik di chat dan lampirkan TTD serta zip kalender:

`/logbook-pkt-staff Nama Lengkap Anda; 1 November 2026 - 30 November 2026`

Opsi tambahan (boleh ditulis di perintah): `kalender: Nama Kalender` (pakai satu kalender saja), `libur: 2026-11-12` (tanggal libur nasional/cuti bersama bila tidak terbaca), `cuti: 2026-11-05`, `rapikan` (Claude menulis ulang agenda ke bahasa logbook; lebih boros kuota).

Claude hanya bertanya bila ada masukan wajib yang kurang. Judul agenda dipakai apa adanya.

## Hemat kuota (terutama akun Free)
- Satu chat baru per logbook. Jangan melanjutkan chat lama.
- Paling murah: zip dari Pemotong Kalender. Hindari `.ics` mentah, screenshot banyak, dan `rapikan` saat kuota mepet.
- Hindari revisi lewat chat. Edit langsung di Excel (TTD sudah dihapus dari ruang kerja setelah file jadi, jadi revisi lewat chat butuh TTD dilampirkan ulang).
- Kuota habis di tengah jalan: ulangi perintah yang sama nanti, atau pecah menjadi dua rentang.

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
2. **Hapus chat** ini (menu chat > Hapus). TTD dan kalender sudah dihapus dari ruang kerja Claude, tetapi lampiran masih tersimpan di chat sampai chat dihapus.
3. Jangan menyimpan TTD atau kalender ke Drive bersama akun ini.

## Catatan
- Jika memakai akun bersama (kantor), jangan menyambungkan kalender, Gmail, atau Drive pribadi ke akun itu, dan jangan pakai jalur `akses kalender saya`.
- Kalau hasil belum sesuai, edit manual di Excel. Revisi lewat chat boros kuota dan butuh TTD dilampirkan ulang.
- Opsional: sebelum memakai skill, matikan *Generate memory from chats* di Settings agar chat ini tidak ikut memori.
