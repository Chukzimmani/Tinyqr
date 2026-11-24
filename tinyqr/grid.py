"""Step 4: the grid. Landmarks first, then the zigzag snake of message bits.

grid[row][col] is 1 for dark and 0 for light.
reserved[row][col] is True for landmark squares the message must not touch.
"""

ALIGNMENT_CENTRES = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26]}


def size_for(version):
    return 17 + 4 * version          # version 1 = 21 wide, version 2 = 25 wide


def empty_grid(version):
    n = size_for(version)
    return [[0] * n for _ in range(n)], [[False] * n for _ in range(n)]


def _set(grid, reserved, row, col, dark):
    grid[row][col] = 1 if dark else 0
    reserved[row][col] = True


def add_finder(grid, reserved, top, left):
    """A 7x7 corner square plus its white border (the 1:1:3:1:1 rhythm)."""
    n = len(grid)
    for r in range(-1, 8):
        for c in range(-1, 8):
            rr, cc = top + r, left + c
            if 0 <= rr < n and 0 <= cc < n:
                ring = max(abs(r - 3), abs(c - 3))
                _set(grid, reserved, rr, cc, ring in (0, 1, 3))


def add_landmarks(grid, reserved, version):
    n = len(grid)
    add_finder(grid, reserved, 0, 0)
    add_finder(grid, reserved, 0, n - 7)
    add_finder(grid, reserved, n - 7, 0)

    for i in range(8, n - 8):                    # timing patterns: the dotted rulers
        _set(grid, reserved, 6, i, i % 2 == 0)
        _set(grid, reserved, i, 6, i % 2 == 0)

    centres = ALIGNMENT_CENTRES[version]         # the smaller square for curved paper
    for r in centres:
        for c in centres:
            if reserved[r][c]:                   # skip spots already used by a finder
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    _set(grid, reserved, r + dr, c + dc, max(abs(dr), abs(dc)) != 1)

    for i in range(9):                           # reserve the format strips (filled in later)
        reserved[8][i] = reserved[i][8] = True
    for i in range(8):
        reserved[8][n - 1 - i] = reserved[n - 1 - i][8] = True
    _set(grid, reserved, n - 8, 8, True)          # the one always-dark square


def place_bits(grid, reserved, bits):
    """Snake the bits in, two columns at a time, from the bottom-right corner."""
    n = len(grid)
    i = 0
    right = n - 1
    while right > 0:
        if right == 6:                            # hop over the vertical timing line
            right = 5
        upward = ((right + 1) & 2) == 0
        for step in range(n):
            row = n - 1 - step if upward else step
            for col in (right, right - 1):
                if not reserved[row][col]:
                    grid[row][col] = int(bits[i]) if i < len(bits) else 0
                    i += 1
        right -= 2
    return grid
