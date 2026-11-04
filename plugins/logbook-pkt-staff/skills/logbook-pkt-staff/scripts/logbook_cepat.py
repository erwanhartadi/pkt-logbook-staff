#!/usr/bin/env python3
"""Mode cepat (hemat token): kalender -> logbook .xlsx + laporan ringkas, dengan satu perintah.

Judul agenda dipakai apa adanya (tanpa Claude menulis ulang). TTD dan berkas kalender
dihapus otomatis; berkas perantara dibuat di folder sementara lalu dibuang.

Pemakaian:
  python logbook_cepat.py --nama "Nama Lengkap" --start 2026-11-02 --end 2026-11-30 \
      --ttd ttd.png --ics ekspor.zip [--ics lain.ics] [--gcal-json gcal_events.json] \
      [--hapus-juga shot1.png shot2.png] [--pakai "Kerja"] [--libur 2026-11-12=Nama] [--cuti 2026-11-05] [--out DIR]

Keluaran: baris 'BERKAS: <path>' lalu teks laporan ringkas untuk disampaikan apa adanya.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
ABAIKAN = ["Birthdays", "Ulang tahun"]
MERAH_JUDUL = re.compile(r"cuti bersama|collective leave|libur", re.I)


def tgl(s):
    d = date.fromisoformat(s)
    return f"{d.day} {BLN[d.month - 1]}"


def pot(t, n=42):
    t = " ".join(str(t).split())
    return t if len(t) <= n else t[: n - 1] + "…"


def run(cmd):
    r = subprocess.run([sys.executable, "-I", *map(str, cmd)], capture_output=True, text=True)
    if r.returncode:
        sys.exit("GAGAL: " + (r.stderr.strip() or r.stdout.strip())[-600:])
    return r.stdout


def pasangan(items):
    out = {}
    for x in items or []:
        k, _, v = x.partition("=")
        out[k.strip()] = v.strip() or "Libur"
    return out


def susun_agenda(ev, nama, libur_manual, cuti_manual):
    keg, dibuang, seen = {}, {}, set()
    for k in ev["kandidat"]:
        cat = " ".join(k["catatan"])
        judul = " ".join(k["judul"].split())
        if "kemungkinan bukan kegiatan kerja" in cat:
            dibuang[str(k["id"])] = "diduga bukan kegiatan kerja"
            continue
        if "ditandai 'free'" in cat:
            dibuang[str(k["id"])] = "ditandai 'free' di kalender"
            continue
        key = (k["tanggal"], judul.lower())
        if key in seen:
            dibuang[str(k["id"])] = "judul sama di hari yang sama"
            continue
        seen.add(key)
        keg.setdefault(k["tanggal"], []).append({"teks": judul, "ids": [k["id"]]})
    libur = {**ev["libur_kandidat_dari_ics"], **libur_manual}
    cuti_bersama = dict(ev["cuti_bersama_kandidat_dari_ics"])
    cuti = set(cuti_manual)
    for d, judul in ev["cuti_pribadi_kandidat"].items():
        (cuti_bersama.__setitem__(d, judul) if MERAH_JUDUL.search(judul) else cuti.add(d))
    return {"nama": nama, "kegiatan": keg, "dibuang": dibuang, "libur": libur,
            "cuti_bersama": cuti_bersama, "cuti_pribadi": sorted(cuti)}


def render(rep, ev, nama):
    L = [f"Logbook {nama}, {rep['periode']}: {rep['butir_dimasukkan']} butir; perkiraan "
         f"{rep['hari_kerja_perkiraan']} hari kerja (isi 'Total hari kerja' manual)."]
    kal = [f"{k.get('nama_kalender') or k['berkas']} ({k['agenda_di_rentang']})"
           for k in ev.get("kalender", []) if k.get("dipakai") and k.get("agenda_di_rentang")]
    if kal:
        L.append("Kalender dipakai: " + ", ".join(kal) + ".")
    merah = rep["libur_merah"]
    if merah:
        L.append("Merah (libur): " + ", ".join(f"{tgl(d)} {pot(n, 30)}" for d, n in merah.items()) +
                 ". Salah? Beri tahu tanggalnya.")
    else:
        L.append("Libur nasional: tidak terdeteksi dari kalender. Sebutkan tanggalnya bila ada.")
    if rep["cuti_pribadi_kuning"]:
        L.append("Kuning (cuti): " + ", ".join(tgl(d) for d in rep["cuti_pribadi_kuning"]) + ".")
    tm = rep.get("tidak_masuk", [])
    if tm:
        L.append(f"Tidak masuk ({len(tm)}):")
        L += [f"- {tgl(x['tanggal'])} {x['jam']} {pot(x['judul'])} ({x['alasan']})" for x in tm[:8]]
        if len(tm) > 8:
            L.append(f"- +{len(tm) - 8} lainnya")
    pw = rep.get("peringatan", [])
    if pw:
        L.append(f"Periksa ({len(pw)}):")
        L += [f"- {tgl(x['tanggal'])} {x['jam']} {pot(x['judul'])}: {pot('; '.join(x['catatan']), 70)}" for x in pw[:8]]
        if len(pw) > 8:
            L.append(f"- +{len(pw) - 8} lainnya")
    kosong = rep["hari_kerja_kosong"]
    if kosong:
        L.append("Hari kerja tanpa kegiatan (isi manual): " + ", ".join(tgl(d) for d in kosong[:10]) +
                 (f", +{len(kosong) - 10} lainnya" if len(kosong) > 10 else "") + ".")
    if rep.get("tanggal_tidak_tercakup"):
        tt = rep["tanggal_tidak_tercakup"]
        L.append("Belum tercakup screenshot: " + ", ".join(tgl(d) for d in tt[:10]) +
                 (f", +{len(tt) - 10} lainnya" if len(tt) > 10 else "") + ". Kirim screenshot tambahan bila ada.")
    for w in ev.get("peringatan_baca", [])[:3]:
        L.append("Catatan: " + pot(w, 100))
    if rep.get("gagal_dihapus"):
        L.append("PERHATIAN: gagal menghapus " + ", ".join(Path(p).name for p in rep["gagal_dihapus"]) + ".")
    L.append("TTD dan kalender sudah dihapus dari ruang kerja. Lampiran masih ada di chat ini: unduh file, lalu hapus chat.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nama", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--ttd", required=True)
    ap.add_argument("--ics", nargs="*", default=[])
    ap.add_argument("--gcal-json", nargs="*", default=[])
    ap.add_argument("--pakai", nargs="*", default=[])
    ap.add_argument("--email", nargs="*", default=[])
    ap.add_argument("--libur", nargs="*", default=[], help="YYYY-MM-DD atau YYYY-MM-DD=Nama")
    ap.add_argument("--cuti", nargs="*", default=[], help="tanggal cuti pribadi YYYY-MM-DD")
    ap.add_argument("--hapus-juga", nargs="*", default=[], help="berkas lain yang dihapus setelah selesai (mis. screenshot)")
    ap.add_argument("--out", default=".")
    ap.add_argument("--simpan-ttd", action="store_true")
    a = ap.parse_args()
    if not a.ics and not a.gcal_json:
        sys.exit("GAGAL: beri --ics (zip/.ics) atau --gcal-json.")

    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        ev_p, ag_p = t / "events.json", t / "agenda.json"
        cmd = [HERE / "ics_events.py", "--start", a.start, "--end", a.end, "--out", ev_p, "--abaikan", *ABAIKAN]
        if a.ics:
            cmd += ["--ics", *a.ics]
        if a.gcal_json:
            cmd += ["--gcal-json", *a.gcal_json]
        if a.pakai:
            cmd += ["--pakai", *a.pakai]
        if a.email:
            cmd += ["--email", *a.email]
        run(cmd)
        ev = json.loads(ev_p.read_text(encoding="utf-8"))
        ag_p.write_text(json.dumps(susun_agenda(ev, a.nama, pasangan(a.libur), a.cuti), ensure_ascii=False), encoding="utf-8")
        bcmd = [HERE / "build.py", "--start", a.start, "--end", a.end, "--agenda", ag_p, "--ttd", a.ttd,
                "--events", ev_p, "--out", a.out, "--hapus", *a.ics, *a.gcal_json, *a.hapus_juga]
        if a.simpan_ttd:
            bcmd.append("--simpan-ttd")
        rep = json.loads(run(bcmd))
    print("BERKAS: " + rep["output"])
    print(render(rep, ev, a.nama))


if __name__ == "__main__":
    main()
