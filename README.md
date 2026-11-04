# pkt-logbook-staff

Skill Claude untuk menyusun **logbook harian staf PKT UGM** (.xlsx) dari file kalender (.ics). Hasilnya berupa file logbook dan laporan agenda yang masuk, tidak masuk, dan perlu dicek.

- Tanda tangan dan file kalender dipakai sekali, lalu dihapus dari ruang kerja Claude.
- Tidak ada data pribadi di repo ini. Jangan pernah meng-commit file `.ics`, tanda tangan, atau logbook terisi (sudah dicegah `.gitignore`).

## Cara pakai (ringkas)
1. Buka **chat baru biasa** di akun Claude pribadi Anda (**bukan Incognito**: Incognito tidak bisa membuat file).
2. Ketik dan lampirkan TTD (gambar tanda tangan):

   `/logbook-pkt-staff "Nama Lengkap Anda" "2 November 2026 - 30 November 2026"`
3. Sumber agenda, pilih satu:
   - **Opsi 1**: lampirkan 4-6 screenshot Google Calendar tampilan Week.
   - **Opsi 2**: tambahkan `akses kalender saya` (Google Calendar pribadi yang tersambung).
4. Periksa laporan singkat, unduh file, lalu **hapus chat**. Detail: [panduan staf](docs/PANDUAN-STAF.md).

Opsi tambahan (boleh): `libur: 2026-11-12`, `cuti: 2026-11-05`, `kalender: Nama`, `rapikan`. Cadangan: zip ekspor Google Calendar (jangan diekstrak), opsional dipotong dengan [Pemotong Kalender](dist/pemotong-kalender.html).

## Mode hemat (bawaan)
Satu perintah skrip membaca agenda, memakai judul apa adanya, mengisi template, menghapus TTD/screenshot/data kalender, dan menampilkan laporan ringkas (maks. 8 baris per daftar). Claude tidak menulis ulang tiap agenda dan tidak bertanya panjang. Agenda ditolak/free/bukan kerja, judul kembar, dan kalender Birthdays tidak dimasukkan, tetapi dilaporkan. `rapikan` = Claude menulis ulang agenda (lebih boros).

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

## Catatan akun Free (hemat kuota)
- Satu chat baru untuk satu logbook. Jangan melanjutkan chat lama yang sudah panjang.
- Paling murah: opsi 2 (akses kalender). Screenshot sedikit lebih boros; hindari `rapikan` dan `.ics` mentah bila kuota mepet.
- Hindari revisi bolak-balik. Edit manual di Excel lebih murah (TTD sudah dihapus setelah file jadi).
- Libur nasional dibaca dari kalender *Holidays in Indonesia* bila ikut terekspor; bila tidak, tulis `libur: 2026-11-12` di perintah.
- Kuota habis di tengah jalan: ulangi perintah yang sama setelah kuota pulih, atau pecah per dua minggu.

## Kebutuhan
Python 3 dengan `openpyxl`, `pillow`, dan `python-dateutil` (biasanya sudah tersedia di lingkungan code execution Claude; jika belum, skill akan memasangnya lewat `pip`).

## Screenshot kalender mingguan
Alternatif tanpa ekspor dan tanpa connector: 4-6 screenshot tampilan Week (seluruh jam terlihat). Skill menyalinnya dan menandai butir yang kurang jelas. Lihat [panduan](docs/PANDUAN-STAF.md).

## Pemotong Kalender
`dist/pemotong-kalender.html` adalah satu halaman web yang berjalan sepenuhnya di browser (tanpa unggah, tanpa internet). Ia memotong ekspor kalender menjadi zip kecil berisi agenda pada rentang tanggal yang dipilih, tanpa deskripsi, lokasi, atau peserta lain. Unduh berkasnya (**Download raw file**) lalu buka dengan klik dua kali. Perlu browser yang mendukung `DecompressionStream` (Chrome/Edge/Safari terbaru, Firefox 113+).

## Akun pribadi vs akun bersama
Di akun pribadi dengan Google Calendar tersambung, tulis `akses kalender saya` pada perintah agar skill membaca kalender tanpa ekspor ICS (hanya rentang tanggal yang diminta, setelah konfirmasi akun). Di akun bersama gunakan ICS; jangan menyambungkan kalender, Gmail, atau Drive pribadi ke akun bersama.

## Privasi
- Skill tidak menyimpan nama, TTD, atau agenda ke memory.
- TTD dan ICS dihapus dari ruang kerja setelah file jadi, **tetapi lampiran masih ada di chat** sampai chat dihapus. Karena itu hapus chat setelah mengunduh file. Incognito tidak bisa dipakai karena tidak dapat membuat file. Opsional: matikan *Generate memory from chats* di Settings sebelum memakai skill.
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
