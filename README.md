# pkt-logbook-staff

Skill Claude untuk menyusun **logbook harian staf PKT UGM** (.xlsx) dari file kalender (.ics). Hasilnya berupa file logbook dan laporan agenda yang masuk, tidak masuk, dan perlu dicek.

- Tanda tangan dan file kalender dipakai sekali, lalu dihapus dari ruang kerja Claude.
- Tidak ada data pribadi di repo ini. Jangan pernah meng-commit file `.ics`, tanda tangan, atau logbook terisi (sudah dicegah `.gitignore`).

## Cara pakai (ringkas)
1. Ekspor kalender Anda ([panduan](docs/PANDUAN-STAF.md)). Lampirkan sebagai **zip** (jangan `.ics` hasil ekstrak, karena bisa melebihi batas chat). Disarankan dipotong dulu per rentang tanggal dengan [Pemotong Kalender](dist/pemotong-kalender.html).
2. Buka **Incognito chat** di Claude.
3. Ketik dan lampirkan TTD (gambar) serta file `.ics`:

   `/logbook-pkt-staff Nama Lengkap Anda; 1 November 2026 - 30 November 2026`
4. Periksa laporan, unduh file, lalu **hapus chat**.

## Pemasangan

### Opsi A: Claude (web/desktop/mobile), akun pribadi
Skill tersedia di semua paket, termasuk Free ([sumber](https://support.claude.com/en/articles/12512180-use-skills-in-claude)). Syaratnya fitur *Code execution and file creation* menyala (Settings > Capabilities).

1. Unduh [`dist/logbook-pkt-staff.zip`](dist/logbook-pkt-staff.zip) (di GitHub: buka berkasnya, klik **Download raw file**). Jangan diekstrak.
2. Buka Claude > **Settings** > **Capabilities** > **Skills** > **Upload skill**, pilih zip tersebut.
3. Aktifkan skill `logbook-pkt-staff`. Tes dengan ketik `/logbook-pkt-staff` di chat baru.

Jika menu Skills atau code execution tidak muncul, cek ketersediaannya untuk paket Anda di https://support.claude.com.

### Opsi B: Claude Code (plugin)
```
/plugin marketplace add erwanhartadi/pkt-logbook-staff
/plugin install logbook-pkt-staff@pkt-logbook
```
Skill dipanggil dengan `/logbook-pkt-staff:logbook-pkt-staff Nama; rentang tanggal`. Untuk memperbarui: `/plugin marketplace update pkt-logbook`.

### Opsi C: Claude Code (salin manual)
```
git clone https://github.com/erwanhartadi/pkt-logbook-staff.git
cp -r pkt-logbook-staff/plugins/logbook-pkt-staff/skills/logbook-pkt-staff ~/.claude/skills/
```

## Catatan akun Free
- Batas pemakaian lebih kecil. Jika kuota habis di tengah proses, coba per dua minggu.
- Pencarian web mungkin tidak tersedia; siapkan daftar libur nasional bulan itu agar bisa diketik ke Claude.

## Kebutuhan
Python 3 dengan `openpyxl`, `pillow`, dan `python-dateutil` (biasanya sudah tersedia di lingkungan code execution Claude; jika belum, skill akan memasangnya lewat `pip`).

## Pemotong Kalender
`dist/pemotong-kalender.html` adalah satu halaman web yang berjalan sepenuhnya di browser (tanpa unggah, tanpa internet). Ia memotong ekspor kalender menjadi zip kecil berisi agenda pada rentang tanggal yang dipilih, tanpa deskripsi, lokasi, atau peserta lain. Unduh berkasnya (**Download raw file**) lalu buka dengan klik dua kali. Perlu browser yang mendukung `DecompressionStream` (Chrome/Edge/Safari terbaru, Firefox 113+).

## Akun pribadi vs akun bersama
Di akun pribadi dengan Google Calendar tersambung, tulis `akses kalender saya` pada perintah agar skill membaca kalender tanpa ekspor ICS (hanya rentang tanggal yang diminta, setelah konfirmasi akun). Di akun bersama gunakan ICS; jangan menyambungkan kalender, Gmail, atau Drive pribadi ke akun bersama.

## Privasi
- Skill tidak menyimpan nama, TTD, atau agenda ke memory.
- TTD dan ICS dihapus dari ruang kerja setelah file jadi, **tetapi lampiran masih ada di chat** sampai chat dihapus. Karena itu pakai Incognito dan hapus chat setelah mengunduh.
- Berkas logbook yang diunduh memuat gambar TTD. Simpan seperlunya.

## Isi repo
- `plugins/logbook-pkt-staff/skills/logbook-pkt-staff/`: skill (instruksi, skrip, template).
- `dist/logbook-pkt-staff.zip`: paket untuk diunggah di Claude (Opsi A). Dibuat ulang setiap kali skill berubah.
- `dist/pemotong-kalender.html`: pemotong kalender di browser (opsional, disarankan).
- `docs/PANDUAN-STAF.md`: panduan satu halaman untuk staf.
- `tools/`: uji pemotong kalender (Node + Python).
- `docs/CONTEXT.md`: konteks dan keputusan desain untuk pemelihara.

## Uji (pemelihara)
```
python plugins/logbook-pkt-staff/skills/logbook-pkt-staff/scripts/selftest.py   # harus mencetak OK
```
Uji memakai data fiktif. Pemotong kalender: `python tools/selftest_pemotong.py` (butuh Node 20+; memastikan hasil skill dari kalender penuh dan terpotong identik). Setelah mengubah skill, bangun ulang `dist/logbook-pkt-staff.zip` (folder `logbook-pkt-staff` di akar zip).

## Pemelihara
Template memuat nama Direktur PKT pada footer "Mengetahui". Ubah di `templates/kosong.xlsx` bila direktur berganti.
