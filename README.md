# Tiny QR

A QR code maker written from scratch in plain Python, one step at a time.

Companion code for the Math With Chukz video **"How QR Codes Work: I Built a Tiny One to Find Out"**.

## Run it

```bash
pip install pillow
python make_qr.py "MATH WITH CHUKZ"
```

It prints every step and saves `qr.png`:

```
Mode: alphanumeric   Level: H   Version: 2 (25 x 25)
Letters -> numbers: M=22 A=10 T=29 H=17  =36 ...
Bytes: 44 total = 16 message + 28 protection
  mask 0: penalty 482
  ...
Winner: mask 1 (penalty 454)
```

Options: `--level L|M|Q|H` (how much protection, default `H`) and `--out file.png`.

Then try damaging it on purpose (needs `pip install opencv-python`):

```bash
python damage_test.py qr.png
```

## How it works (the same steps as the video)

| Step | File | What happens |
|---|---|---|
| 1. Letters to numbers to bits | `tinyqr/encode.py` | Each character gets a number from a fixed table (M = 22, A = 10, ...), pairs become 11 bits, plus a header and padding |
| 2. Error correction | `tinyqr/reed_solomon.py` | Reed–Solomon adds extra "protection" bytes, using wrap-around arithmetic on 0–255 |
| 3. Landmarks and the zigzag | `tinyqr/grid.py` | Corner squares, timing rulers, alignment square, then the bits snake in two columns at a time from the bottom-right |
| 4. Masks | `tinyqr/masks.py` | Try all 8 masks, score each with the 4 penalty rules, keep the lowest |

Supports versions 1–4 (21×21 up to 33×33), all four levels L, M, Q and H, and alphanumeric or byte mode. Every combination was checked with two independent scanners.
