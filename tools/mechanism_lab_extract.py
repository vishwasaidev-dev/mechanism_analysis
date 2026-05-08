#!/usr/bin/env python3
"""Build contact sheets from scanned mechanism PDFs for rapid mechanism mining."""
from __future__ import annotations
import argparse, math
from pathlib import Path
import fitz
from PIL import Image, ImageDraw


def contact_sheet(pdf: Path, out: Path, start: int, stop: int, step: int, zoom: float = 0.28):
    doc = fitz.open(pdf)
    pages = list(range(max(0, start - 1), min(stop, doc.page_count), step))
    thumbs = []
    for idx in pages:
        pix = doc[idx].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        im.thumbnail((170, 225))
        tile = Image.new('RGB', (190, 260), 'white')
        tile.paste(im, ((190 - im.width) // 2, 24))
        d = ImageDraw.Draw(tile)
        d.text((8, 6), f'p{idx + 1}', fill=(0, 0, 0))
        thumbs.append(tile)
    cols = 5
    rows = max(1, math.ceil(len(thumbs) / cols))
    sheet = Image.new('RGB', (cols * 190, rows * 260), (232, 236, 242))
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i % cols) * 190, (i // cols) * 260))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--stop', type=int, default=200)
    ap.add_argument('--step', type=int, default=10)
    ap.add_argument('--out-dir', default='generated/mechanism_lab/contact_sheets')
    args = ap.parse_args()
    pdf = Path(args.pdf)
    out = Path(args.out_dir) / f'{pdf.stem}_p{args.start}_{args.stop}_step{args.step}.png'
    print(contact_sheet(pdf, out, args.start, args.stop, args.step))

if __name__ == '__main__':
    main()
