# Panduan: Logbook PKT dengan Claude (1 halaman)

## Sebelum mulai
1. Pasang skill sekali saja (lihat README). Pastikan *Code execution and file creation* menyala (Settings > Capabilities).
2. Buka **chat baru biasa** di akun Claude pribadi Anda. **Jangan Incognito**: Incognito tidak bisa membuat file.
3. Siapkan **TTD**: foto/scan tanda tangan di kertas putih (PNG/JPG). Beri nama file `ttd`.

## Perintah
Ketik, lalu lampirkan TTD dan sumber agenda:

`/logbook-pkt-staff "Nama Lengkap Anda" "2 November 2026 - 30 November 2026"`

**Opsi 1: screenshot kalender** (lampirkan 4-6 gambar)
1. Buka Google Calendar, tampilan **Week**. Centang hanya kalender kerja Anda (dan *Holidays in Indonesia* agar libur terbaca).
2. Seluruh jam **00:00-24:00** harus terlihat: perkecil browser (Ctrl/Cmd + minus) atau ambil dua screenshot per minggu. Tanggal dan nama bulan di atas ikut terlihat.
3. Satu screenshot per minggu. Judul sering terpotong? Coba tampilan **Schedule**.
4. Lampirkan semua gambar bersama TTD.

**Opsi 2: akses Google Calendar** (hanya akun pribadi dengan Google Calendar tersambung di Connectors)
Tambahkan `akses kalender saya` pada perintah. Claude menyebut akun kalender yang tersambung dan meminta konfirmasi, lalu hanya membaca rentang tanggal Anda. **Jangan dipakai di akun bersama.**

Opsi tambahan di perintah (boleh): `libur: 2026-11-12`, `cuti: 2026-11-05`, `kalender: Nama Kalender`, `rapikan` (agenda ditulis ulang ke bahasa logbook; lebih boros kuota).

## Hasil
- **File logbook (.xlsx)**: merah = akhir pekan/libur (tanpa TTD), kuning = cuti.
- **Laporan singkat**: jumlah butir, libur dan cuti yang terdeteksi, agenda yang tidak masuk beserta alasan, butir yang perlu diperiksa, hari kerja kosong, dan tanggal yang belum tercakup screenshot.

Periksa laporan. Isi manual hari kosong dan kolom "Total hari kerja". Judul agenda dipakai apa adanya.

## Hemat kuota (akun Free)
- Satu chat baru per logbook; jangan lanjutkan chat lama.
- Opsi 2 paling murah, screenshot sedikit lebih boros, `rapikan` paling boros.
- Hindari revisi lewat chat; edit langsung di Excel.
- Kuota habis di tengah jalan: ulangi perintah yang sama nanti, atau pecah menjadi dua rentang.

## Setelah selesai (wajib)
1. **Unduh** file logbook.
2. **Hapus chat** ini. TTD, screenshot, dan data kalender sudah dihapus dari ruang kerja Claude, tetapi lampiran masih tersimpan di chat sampai chat dihapus.
3. Opsional: sebelum mulai, matikan *Generate memory from chats* di Settings.
4. Jangan menyimpan TTD atau kalender ke Drive bersama.

## Keterbatasan
Agenda yang Anda tolak biasanya tidak tampil di screenshot dan tidak bisa dicek; judul terpotong ditandai "periksa". Jika tidak punya screenshot atau akses kalender, ekspor `.zip` Google Calendar masih bisa dilampirkan (jangan diekstrak; opsional dipotong dengan `dist/pemotong-kalender.html`).
