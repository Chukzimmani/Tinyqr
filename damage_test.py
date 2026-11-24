"""Tear a piece off a QR code on purpose, then check it still scans.

    python damage_test.py qr.png

Needs:  pip install opencv-python
It whites out a block near the right edge and scribbles a line across the
middle (never touching the three corner squares), then tries to read it.
"""

import sys

import cv2

path = sys.argv[1] if len(sys.argv) > 1 else "qr.png"
img = cv2.imread(path)
h, w = img.shape[:2]

# A "torn" block on the right edge, between the top-right and bottom corner squares
cv2.rectangle(img, (int(w * 0.70), int(h * 0.42)), (w, int(h * 0.62)), (255, 255, 255), -1)
# A marker scribble across the middle
cv2.line(img, (int(w * 0.35), int(h * 0.72)), (int(w * 0.62), int(h * 0.45)), (0, 0, 0), max(3, w // 30))

cv2.imwrite("damaged.png", img)
text, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
print("Saved damaged.png")
print("Scanner reads:", repr(text) if text else "nothing (too much damage)")
