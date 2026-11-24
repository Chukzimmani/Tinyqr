"""Make a QR code from scratch and show every step.

    python make_qr.py "MATH WITH CHUKZ"
    python make_qr.py "MATH WITH CHUKZ" --level H --out chukz.png
"""

import argparse

from tinyqr import make_qr, save_png

parser = argparse.ArgumentParser(description="Tiny QR code maker")
parser.add_argument("message")
parser.add_argument("--level", default="H", choices="LMQH")
parser.add_argument("--out", default="qr.png")
args = parser.parse_args()

grid, info = make_qr(args.message, args.level, verbose=True)
save_png(grid, args.out)
print(f"Saved {args.out}")
