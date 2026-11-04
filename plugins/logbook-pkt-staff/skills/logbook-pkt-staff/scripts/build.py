#!/usr/bin/env python3
"""Isi logbook PKT dari agenda JSON, buat laporan, lalu hapus TTD/ICS (sekali pakai).

Pemakaian:
  python build.py --start 2026-11-02 --end 2026-11-30 --agenda agenda.json \
      --ttd ttd.png [--events events.json] [--hapus FILE ...] [--out DIR]

Format agenda.json:
{
  "nama": "Nama Lengkap Staf",                      # wajib
  "kegiatan": {"2026-11-02": ["Rapat koordinasi tim",
                              {"teks": "Diskusi proposal", "ids": [2, 3]}]},
  "dibuang": {"7": "acara pribadi"},                # id kandidat yang sengaja tidak dimasukkan
  "libur": {"2026-12-25": "Hari Raya Natal"},       # merah
  "cuti_bersama": {"2026-12-24": "Cuti bersama"},   # merah
  "cuti_pribadi": ["2026-11-17"]                    # kuning
}
Butir bisa string atau {"teks", "ids"}; "ids" mengacu ke id di events.json agar laporan akurat.
"""
import argparse
import io
import json
import math
import os
import re
import sys
from copy import copy
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Alignment, PatternFill
from PIL import Image as PILImage, ImageChops

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "templates" / "kosong.xlsx"

FIRST_ROW, TEMPLATE_ROWS = 6, 26
DATE_FMT = r"[$-3809]dd\ mmmm\ yyyy;@"
RED = PatternFill("solid", fgColor="FFFF0000")
YELLOW = PatternFill("solid", fgColor="FFFFFF00")
NO_FILL = PatternFill(fill_type=None)

EMU_PER_PX, EMU_PER_PT = 9525, 12700
TTD_CX, TTD_CY = 634680, 507600
COL_D_EMU = int((15.6640625 * 7 + 5) * EMU_PER_PX)

CHARS_PER_LINE, PT_PER_LINE, PAD_PT = 46, 15.5, 6
MIN_H_EMPTY, MIN_H_SIGNED = 21, 44

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]


def fmt_tgl(d, with_year=True):
    s = f"{d.day} {BULAN[d.month - 1]}"
    return f"{s} {d.year}" if with_year else s


def fmt_periode(a, b):
    return f"{fmt_tgl(a, a.year != b.year)} - {fmt_tgl(b)}"


def prep_ttd(path, transparent):
    im = PILImage.open(path).convert("RGBA")
    im.thumbnail((3 * TTD_CX // EMU_PER_PX, 3 * TTD_CY // EMU_PER_PX))
    if transparent:
        ink = im.convert("L").point(lambda v: 0 if v > 235 else 255)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), ink))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def add_ttd(ws, row, png, height_pt):
    img = XLImage(io.BytesIO(png))
    col_off = max((COL_D_EMU - TTD_CX) // 2, 0)
    row_off = max(int((height_pt * EMU_PER_PT - TTD_CY) / 2), 0)
    img.anchor = OneCellAnchor(
        _from=AnchorMarker(col=3, colOff=col_off, row=row - 1, rowOff=row_off),
        ext=XDRPositiveSize2D(TTD_CX, TTD_CY))
    ws.add_image(img)


def row_height(items, signed):
    lines = sum(max(1, math.ceil((len(t) + 2) / CHARS_PER_LINE)) for t in items)
    h = lines * PT_PER_LINE + PAD_PT if items else 0
    return max(h, MIN_H_SIGNED if signed else MIN_H_EMPTY)


def parse_dates(d):
    return {date.fromisoformat(k): v for k, v in d.items()}


def expand_rows(ws, n_days):
    extra = n_days - TEMPLATE_ROWS
    if extra <= 0:
        return
    last = FIRST_ROW + TEMPLATE_ROWS - 1
    old_h = {r: ws.row_dimensions[r].height for r in range(last + 1, ws.max_row + 1)}
    ws.insert_rows(last + 1, extra)
    for r, h in old_h.items():
        ws.row_dimensions[r + extra].height = h
    for r in range(last + 1, last + 1 + extra):
        ws.row_dimensions[r].height = None
        for col in range(1, 5):
            ws.cell(r, col)._style = copy(ws.cell(last, col)._style)


def fill_sheet(ws, days, data, png):
    keg, merah, kuning = data["teks"], data["merah"], data["kuning"]
    ws["C2"] = f": {data['nama']}"
    ws["C3"] = f": {fmt_periode(days[0], days[-1])}"
    for i in range(max(TEMPLATE_ROWS, len(days))):
        r = FIRST_ROW + i
        a, b, c, d = (ws.cell(r, k) for k in range(1, 5))
        if i >= len(days):
            a.value = b.value = c.value = None
            for x in (c, d):
                x.fill = NO_FILL
            ws.row_dimensions[r].height = MIN_H_EMPTY
            continue
        day = days[i]
        items = keg.get(day, [])
        a.value = i + 1
        b.value = datetime(day.year, day.month, day.day)
        b.number_format = DATE_FMT
        c.value = "\n".join(f"> {t}" for t in items) or None
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        is_red = day.weekday() >= 5 or day in merah
        fill = RED if is_red else YELLOW if day in kuning else NO_FILL
        for x in (c, d):
            x.fill = fill
        signed = not is_red
        h = row_height(items, signed)
        ws.row_dimensions[r].height = h
        if signed:
            add_ttd(ws, r, png, h)


def wipe(path):
    """Timpa dengan nol lalu hapus. Mengembalikan True bila berhasil."""
    try:
        p = Path(path)
        if not p.is_file():
            return False
        with open(p, "r+b") as f:
            f.write(b"\0" * p.stat().st_size)
            f.flush()
            os.fsync(f.fileno())
        p.unlink()
        return True
    except Exception:
        return False


def normalisasi_item(x):
    if isinstance(x, str):
        return x.strip(), []
    return str(x.get("teks", "")).strip(), [int(i) for i in x.get("ids", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--agenda", required=True)
    ap.add_argument("--ttd", required=True, help="gambar TTD (dipakai sekali)")
    ap.add_argument("--events", help="events.json dari ics_events.py (untuk laporan)")
    ap.add_argument("--hapus", nargs="*", default=[],
                    help="berkas yang dihapus setelah xlsx jadi (mis. ICS); TTD selalu ikut dihapus")
    ap.add_argument("--simpan-ttd", action="store_true", help="jangan hapus TTD (untuk uji)")
    ap.add_argument("--out", default=".")
    ap.add_argument("--no-transparan", action="store_true")
    a = ap.parse_args()

    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    if end < start:
        sys.exit("tanggal_selesai < tanggal_mulai")
    raw = json.loads(Path(a.agenda).read_text(encoding="utf-8"))
    nama = str(raw.get("nama", "")).strip()
    if not nama:
        sys.exit("Field 'nama' di agenda.json wajib diisi (nama lengkap staf).")
    if not Path(a.ttd).is_file():
        sys.exit(f"File TTD tidak ditemukan: {a.ttd}")

    libur = parse_dates(raw.get("libur", {}))
    cuti_bersama = parse_dates(raw.get("cuti_bersama", {}))
    kegiatan = {}
    refs = set()
    for k, items in raw.get("kegiatan", {}).items():
        teks = []
        for it in items:
            t, ids = normalisasi_item(it)
            if t:
                teks.append(t)
                refs.update(ids)
        kegiatan[date.fromisoformat(k)] = teks
    data = {
        "nama": nama,
        "teks": kegiatan,
        "merah": set(libur) | set(cuti_bersama),
        "kuning": {date.fromisoformat(x) for x in raw.get("cuti_pribadi", [])},
    }

    out_dir = Path(a.out).resolve()
    if out_dir == TEMPLATE.parent:
        sys.exit("Output tidak boleh di folder templates/")
    periode = fmt_periode(start, end)
    aman = re.sub(r'[\\/:*?"<>|]', "-", nama)
    nama_file = f"Logbook_{aman}_{periode}.xlsx"
    out = out_dir / nama_file
    out_dir.mkdir(parents=True, exist_ok=True)

    png = prep_ttd(a.ttd, not a.no_transparan)
    all_days = [start + timedelta(n) for n in range((end - start).days + 1)]
    wb = load_workbook(TEMPLATE)
    ws = wb.worksheets[0]
    expand_rows(ws, len(all_days))
    fill_sheet(ws, all_days, data, png)
    wb.properties.creator = "Logbook PKT"
    wb.properties.lastModifiedBy = "Logbook PKT"
    wb.save(out)
    load_workbook(out)  # pastikan file valid sebelum berkas sumber dihapus

    # ---------- laporan ----------
    merah = data["merah"]

    def hari_merah(d):
        return d.weekday() >= 5 or d in merah

    hari_kerja = [d for d in all_days if not hari_merah(d)]
    kosong = [d.isoformat() for d in hari_kerja if d not in data["kuning"] and not kegiatan.get(d)]
    laporan = {
        "output": str(out), "nama_file": nama_file, "periode": periode, "baris": len(all_days),
        "hari_kerja_perkiraan": len(hari_kerja) - len([d for d in data["kuning"] if d in hari_kerja]),
        "libur_merah": {d.isoformat(): n for d, n in sorted({**libur, **cuti_bersama}.items()) if start <= d <= end},
        "cuti_pribadi_kuning": sorted(d.isoformat() for d in data["kuning"] if start <= d <= end),
        "hari_kerja_kosong": kosong,
        "agenda_di_luar_rentang": sorted(d.isoformat() for d in kegiatan if not start <= d <= end),
        "butir_dimasukkan": sum(len(v) for k, v in kegiatan.items() if start <= k <= end),
    }
    if a.events:
        ev = json.loads(Path(a.events).read_text(encoding="utf-8"))
        dibuang = {int(k): v for k, v in raw.get("dibuang", {}).items()}
        masuk, peringatan, tidak_masuk, belum = [], [], [], []
        for k in ev["kandidat"]:
            d = date.fromisoformat(k["tanggal"])
            if k["id"] in refs:
                masuk.append({"id": k["id"], "tanggal": k["tanggal"], "judul": k["judul"]})
                cat = list(k["catatan"])
                if hari_merah(d):
                    cat.append("jatuh di akhir pekan/hari libur (baris merah, tanpa TTD)")
                if d in data["kuning"]:
                    cat.append("jatuh di hari cuti pribadi")
                cat = [c for c in cat if c != "duplikat digabung"]
                if cat:
                    peringatan.append({"id": k["id"], "tanggal": k["tanggal"], "jam": f"{k['mulai']}-{k['selesai']}",
                                       "judul": k["judul"], "catatan": cat})
            elif k["id"] in dibuang:
                tidak_masuk.append({"tanggal": k["tanggal"], "jam": f"{k['mulai']}-{k['selesai']}",
                                    "judul": k["judul"], "alasan": dibuang[k["id"]]})
            else:
                belum.append({"id": k["id"], "tanggal": k["tanggal"], "jam": f"{k['mulai']}-{k['selesai']}",
                              "judul": k["judul"]})
        for x in ev["dikecualikan"]:
            tidak_masuk.append({"tanggal": x["tanggal"], "jam": f"{x['mulai']}-{x['selesai']}" if x["mulai"] else "seharian",
                                "judul": x["judul"], "alasan": x["alasan"]})
        laporan.update({
            "masuk_agenda_terpetakan": len(masuk),
            "tidak_masuk": sorted(tidak_masuk, key=lambda z: z["tanggal"]),
            "peringatan": peringatan,
            "belum_terpetakan_periksa": belum,
            "duplikat_digabung": ev.get("duplikat_digabung", 0),
            "di_luar_rentang_diabaikan": ev.get("di_luar_rentang", 0),
            "tanggal_tidak_tercakup": ev.get("tanggal_tidak_tercakup", []),
            "peringatan_baca_ics": ev.get("peringatan_baca", []),
        })

    # ---------- hapus berkas sensitif ----------
    target = list(a.hapus) + ([] if a.simpan_ttd else [a.ttd])
    laporan["dihapus"] = [t for t in target if wipe(t)]
    laporan["gagal_dihapus"] = [t for t in target if t not in laporan["dihapus"]]
    print(json.dumps(laporan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
