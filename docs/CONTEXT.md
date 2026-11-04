# Konteks proyek: logbook-pkt-staff

Berkas ini untuk sesi Claude Code berikutnya. Baca dulu supaya tidak mengulang diskusi.

## Tujuan
Varian skill `logbook-pkt` yang bisa dipakai staf lain di PKT (Center for Tropical Medicine, FK-KMK UGM) lewat akun Claude kantor.

## Keputusan yang sudah final
- Akun kantor: **satu akun bersama, paket Pro**. Tidak ada provisioning organisasi. Skill diunggah manual sebagai zip (Settings > Capabilities > Skills).
- Format logbook PKT **sama untuk semua staf** (template `templates/kosong.xlsx`).
- Sumber jadwal: **file ICS** yang diekspor staf dari kalendernya sendiri. Connector kalender, Gmail, dan Drive tidak dipakai di akun bersama. Cadangan: screenshot atau isian manual.
- Panduan satu halaman untuk staf diperlukan, karena sebagian belum pernah ekspor ICS.
- Pemanggilan: `/logbook-pkt-staff Nama Lengkap; rentang tanggal` + lampiran TTD (gambar) dan ICS.
- Keluaran: file logbook xlsx + laporan **masuk / tidak masuk / peringatan**.
- TTD dan ICS dipakai sekali. Salinan di workspace dihapus otomatis setelah file jadi (`build.py --hapus`). Skill tidak menyimpan apa pun ke memory, Drive, atau Gmail.
- Penghapusan chat tidak bisa diotomatisasi skill. Staf diminta memakai **Incognito chat** dan menghapus chat setelah mengunduh file.

## Aturan privasi (WAJIB)
- Paket ini **tidak boleh berisi data pemilik skill asli**: nama, email, NIP, tanda tangan, nama penerima email, ID kalender, nama proyek pribadi.
- Data uji hanya fiktif ("Staf Contoh", `staf.contoh@example.test`, TTD dummy buatan skrip).
- Jangan menyalin `assets/ttd.png`, `templates/contoh-terisi.xlsx`, atau repo `pkt-logbook-skill` ke paket ini.
- Metadata template (creator, lastModifiedBy) sudah dibersihkan. Pertahankan.
- Sebelum zip diserahkan, jalankan pemindaian kebocoran (lihat bagian Pemeriksaan) dan laporkan hasilnya.
- Satu-satunya nama orang di template adalah Direktur PKT pada footer "Mengetahui". Itu bagian format institusi, bukan data pribadi. Ubah di template bila direktur berganti.

## Yang diambil dari skill asli (hanya struktur dan logika)
- Template 26 baris isi (baris 6-31), footer total hari kerja dan blok "Mengetahui".
- Warna: merah untuk Sabtu/Minggu/libur nasional/cuti bersama (tanpa TTD), kuning untuk cuti pribadi (dengan TTD).
- TTD 1,76 x 1,41 cm di tengah kolom D pada hari kerja, latar putih dibuat transparan.
- Gaya ringkasan: butir diawali "> ", kata kerja di depan, 5-12 kata, 3-6 butir per hari, kronologis, jangan mengarang.
- Tinggi baris dihitung dari jumlah baris teks. Baris tabel bertambah otomatis bila rentang melebihi 26 hari.
- "Total hari kerja" dibiarkan "..." (isi manual); skrip hanya melaporkan perkiraan.

## Yang diubah dari skill asli
- Nama wajib diberikan (tanpa nilai bawaan). Tidak ada draft email dan tidak ada penerima.
- Sumber agenda: ICS (skrip `scripts/ics_events.py`), bukan Google Calendar/Spark.
- Laporan eksplisit apa yang masuk dan tidak masuk, dengan alasan. Setiap agenda punya id agar tidak ada yang hilang diam-diam.
- TTD dan ICS dihapus setelah build.

## Struktur
- `SKILL.md`: instruksi untuk Claude (alur, privasi, laporan).
- `scripts/ics_events.py`: ICS -> `events.json` (kandidat + dikecualikan + alasan). Mendukung RRULE, EXDATE, RECURRENCE-ID, zona waktu, status declined/cancelled.
- `scripts/build.py`: agenda JSON + TTD -> xlsx + laporan JSON + hapus berkas sensitif.
- `scripts/selftest.py`: uji ujung ke ujung dengan data fiktif.
- `templates/kosong.xlsx`: template kosong.
- `PANDUAN-STAF.md`: panduan satu halaman.

## Pemeriksaan sebelum diserahkan
1. `python scripts/selftest.py` harus `OK`.
2. Pindai seluruh isi paket (termasuk isi xlsx dan metadata) untuk: nama, email, kata kunci proyek pribadi, nama penerima, dan hash TTD asli. Hasil harus nol temuan.
3. Uji manual dengan 1-2 staf di akun kantor.

## Belum diputuskan / lanjutan
- Konfirmasi ketentuan penggunaan Anthropic untuk akun bersama (jika tidak diperbolehkan, alternatif: paket Team dengan seat per staf).
- Versi Docs/PDF dari panduan staf (saat ini Markdown).

## Temuan uji nyata (4 Nov 2026)
- Ekspor Google Calendar mengunduh **semua kalender dan seluruh riwayat** (zip berisi banyak .ics); tidak bisa dibatasi rentang tanggal.
- Solusi: `ics_events.py` menerima `.zip`, menyaring per rentang, melaporkan ringkasan per kalender, dan `--pakai` memilih kalender. SKILL.md meminta staf memilih kalender bila lebih dari satu punya agenda.
- Skill berlaku di akun Free (dengan code execution); belum diuji di akun Free sungguhan.
- Jalur Google Calendar (connector) ditambahkan atas permintaan: aktif hanya jika staf menulis "akses kalender saya"/"pakai gcal". Claude menulis JSON ringkas (`gcal_events.json`, tanpa deskripsi/lokasi/peserta) lalu `ics_events.py --gcal-json` memakai pipeline dan laporan yang sama. Di akun bersama jalur ini tidak boleh dipakai (kalender yang tersambung milik akun bersama). Belum diuji dengan connector sungguhan; hanya diuji dengan JSON fiktif.
- Uji nyata: melampirkan `.ics` hasil ekstrak (ekspor penuh) langsung ke chat memunculkan "This request exceeds Claude's context limit", karena file teks masuk ke konteks. Zip tidak dimasukkan ke konteks, jadi skill bisa memprosesnya lewat skrip. Solusi: lampirkan zip; atau pakai `dist/pemotong-kalender.html` (JS murni di browser; zip masuk, zip kecil keluar; hanya SUMMARY/waktu/RRULE/EXDATE/RECURRENCE-ID/STATUS/TRANSP dan ATTENDEE milik pemilik yang dipertahankan).
- Aturan pemotong: agenda tunggal disimpan bila beririsan dengan rentang +-3 hari (zona waktu diabaikan, margin menutupnya); agenda berulang disimpan bila mulai sebelum akhir rentang dan UNTIL (jika ada) tidak sebelum awal; override (RECURRENCE-ID) disimpan bila ID-nya atau waktu barunya masuk jendela. `tools/selftest_pemotong.py` membuktikan hasil skill dari kalender penuh dan terpotong identik.
- Jalur screenshot mingguan ditambahkan (SKILL.md 3c): Claude mentranskripsikan gambar ke `gcal_events.json` (skema sama dengan jalur connector) + `tercakup` (rentang tanggal tiap gambar) + `ragu` per agenda. Skrip melaporkan `tanggal_tidak_tercakup` dan menandai butir `ragu`. Risiko utama: jam di luar area terlihat (mis. agenda 03:00 atau 21:00), judul terpotong, agenda yang ditolak tidak tampil. Belum diuji dengan screenshot sungguhan; hanya JSON fiktif.
