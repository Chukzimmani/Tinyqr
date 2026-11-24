"""Step 5: try all eight masks, score each one, keep the lowest penalty.

A mask flips message squares in a fixed pattern. The scanner knows the
pattern, so it can flip them back. The penalty score punishes things that
cameras find hard to read.
"""

MASKS = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]

LEVEL_BITS = {"L": 0b01, "M": 0b00, "Q": 0b11, "H": 0b10}


def apply_mask(grid, reserved, k):
    n = len(grid)
    out = [row[:] for row in grid]
    for r in range(n):
        for c in range(n):
            if not reserved[r][c] and MASKS[k](r, c):
                out[r][c] ^= 1
    return out


def format_bits(level, k):
    """15 bits saying the protection level and the mask number, with their own protection."""
    data = (LEVEL_BITS[level] << 3) | k
    rem = data << 10
    for i in range(14, 9, -1):
        if rem & (1 << i):
            rem ^= 0x537 << (i - 10)
    return ((data << 10) | rem) ^ 0x5412


def write_format(grid, level, k):
    n = len(grid)
    bits = format_bits(level, k)
    bit = lambda i: (bits >> i) & 1
    for i in range(6):
        grid[i][8] = bit(i)
    grid[7][8] = bit(6)
    grid[8][8] = bit(7)
    grid[8][7] = bit(8)
    for i in range(9, 15):
        grid[8][14 - i] = bit(i)
    for i in range(8):
        grid[8][n - 1 - i] = bit(i)
    for i in range(8, 15):
        grid[n - 15 + i][8] = bit(i)
    grid[n - 8][8] = 1
    return grid


def penalty(grid):
    """The four penalty rules from the QR standard. Lower is better."""
    n = len(grid)
    score = 0
    lines = [row for row in grid] + [[grid[r][c] for r in range(n)] for c in range(n)]

    # Rule 1: long runs of the same colour (5 or more in a row)
    for line in lines:
        run = 1
        for i in range(1, n):
            if line[i] == line[i - 1]:
                run += 1
            else:
                if run >= 5:
                    score += 3 + (run - 5)
                run = 1
        if run >= 5:
            score += 3 + (run - 5)

    # Rule 2: solid 2x2 blocks
    for r in range(n - 1):
        for c in range(n - 1):
            if grid[r][c] == grid[r][c + 1] == grid[r + 1][c] == grid[r + 1][c + 1]:
                score += 3

    # Rule 3: patterns that look like a fake corner square (1:1:3:1:1 next to 4 light squares)
    patterns = ([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1])
    for line in lines:
        for i in range(n - 10):
            if line[i:i + 11] in patterns:
                score += 40

    # Rule 4: too much dark or too much light overall
    dark = sum(map(sum, grid))
    percent = dark * 100 / (n * n)
    score += int(abs(percent - 50) // 5) * 10
    return score
