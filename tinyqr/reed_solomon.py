"""Step 3: Reed-Solomon error correction.

The idea from the video: treat the message as points on a curve and send extra
values from the same curve, so missing values can be rebuilt.

QR codes do this with "wrap-around" arithmetic on the numbers 0-255
(a finite field called GF(256)). Adding is XOR, and multiplying uses
tables of powers of a special number called alpha.
"""

# Build the power tables once: EXP[i] = alpha^i, LOG[alpha^i] = i
EXP = [0] * 512
LOG = [0] * 256
x = 1
for i in range(255):
    EXP[i] = x
    LOG[x] = i
    x <<= 1
    if x & 0x100:          # wrap around: reduce by the QR code's special polynomial
        x ^= 0x11D
for i in range(255, 512):
    EXP[i] = EXP[i - 255]


def gf_mul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def generator(n):
    """The curve that all codewords must fit: (x - a^0)(x - a^1)...(x - a^(n-1))."""
    g = [1]
    for i in range(n):
        nxt = [0] * (len(g) + 1)
        for j, coef in enumerate(g):
            nxt[j] ^= coef                    # coef * x
            nxt[j + 1] ^= gf_mul(coef, EXP[i])  # coef * a^i
        g = nxt
    return g


def protection_bytes(data, n):
    """The n extra bytes that protect `data` (polynomial long division remainder)."""
    g = generator(n)
    remainder = list(data) + [0] * n
    for i in range(len(data)):
        factor = remainder[i]
        if factor != 0:
            for j, coef in enumerate(g):
                remainder[i + j] ^= gf_mul(coef, factor)
    return remainder[len(data):]
