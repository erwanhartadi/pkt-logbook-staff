# Mode rapi (hanya jika staf menulis "rapikan"): Claude menulis ulang tiap agenda ke bahasa logbook

Lebih boros kuota. Pakai hanya bila diminta.

1. `python <folder-skill>/scripts/ics_events.py --start <mulai> --end <selesai> --gcal-json gcal_events.json --abaikan Birthdays "Ulang tahun" --out events.json` (atau `--ics <zip>`; JSON dibuat seperti di SKILL.md).
2. Ringkas tiap `kandidat` ke satu butir pendek (5-12 kata), kata kerja di depan ("Rapat ...", "Diskusi ...", "Koordinasi dengan ...", "Menyusun ..."). Nama proyek dan akronim apa adanya. Jangan mengarang; judul ambigu ditulis apa adanya. Buang yang bukan kegiatan kerja (catat di `dibuang` dengan alasan). Setiap butir wajib memuat `ids`; tidak boleh ada kandidat yang tidak dipetakan dan tidak dibuang.
3. Tulis `agenda.json`: `{"nama", "kegiatan": {"YYYY-MM-DD": [{"teks", "ids": [..]}]}, "dibuang": {"id": "alasan"}, "libur": {}, "cuti_bersama": {}, "cuti_pribadi": []}`. Libur dari `libur_kandidat_dari_ics` / `cuti_bersama_kandidat_dari_ics` / `cuti_pribadi_kandidat` di `events.json`, atau dari staf.
4. `python <folder-skill>/scripts/build.py --start <mulai> --end <selesai> --agenda agenda.json --ttd <ttd> --events events.json --hapus <zip/.ics> --out <folder-output>`.
5. Kirim berkas, lalu ringkas laporan JSON secukupnya (masuk, tidak masuk, periksa, hari kosong) dan pengingat unduh lalu hapus chat.
