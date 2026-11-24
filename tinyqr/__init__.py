"""Tiny QR: a QR code maker written from scratch, step by step.

Companion code for the Math With Chukz video
"How QR Codes Work: I Built a Tiny One to Find Out".
"""

from .encode import CAPACITY, pick_mode, choose_version, data_codewords, letters_to_numbers
from .reed_solomon import protection_bytes
from .grid import empty_grid, add_landmarks, place_bits
from .masks import apply_mask, write_format, penalty


def make_qr(message, level="H", verbose=False):
    say = print if verbose else (lambda *a, **k: None)

    # Step 1: letters -> numbers -> bits
    mode = pick_mode(message)
    version = choose_version(message, mode, level)
    say(f"Message: {message!r}")
    say(f"Mode: {mode}   Level: {level}   Version: {version} ({17 + 4 * version} x {17 + 4 * version})")
    if mode == "alphanumeric":
        say("Letters -> numbers:", " ".join(f"{ch}={n}" for ch, n in zip(message, letters_to_numbers(message))))

    # Step 2: header + message + padding -> bytes
    data, bits = data_codewords(message, mode, version, level)
    say(f"Message bits ({len(bits)}): {bits}")

    # Step 3: Reed-Solomon protection, block by block, then interleave
    blocks, per_block, ec_per_block = CAPACITY[(version, level)]
    data_blocks = [data[i * per_block:(i + 1) * per_block] for i in range(blocks)]
    ec_blocks = [protection_bytes(b, ec_per_block) for b in data_blocks]
    final = [b[i] for i in range(per_block) for b in data_blocks] + \
            [b[i] for i in range(ec_per_block) for b in ec_blocks]
    say(f"Bytes: {len(final)} total = {blocks * per_block} message + {blocks * ec_per_block} protection")

    # Step 4: landmarks, then snake the bits into the grid
    grid, reserved = empty_grid(version)
    add_landmarks(grid, reserved, version)
    all_bits = "".join(format(b, "08b") for b in final)
    place_bits(grid, reserved, all_bits)

    # Step 5: try all eight masks and keep the lowest penalty score
    scores = []
    for k in range(8):
        candidate = write_format(apply_mask(grid, reserved, k), level, k)
        scores.append((penalty(candidate), k, candidate))
        say(f"  mask {k}: penalty {scores[-1][0]}")
    best_score, best_mask, best = min(scores, key=lambda s: (s[0], s[1]))
    say(f"Winner: mask {best_mask} (penalty {best_score})")
    return best, {"mode": mode, "version": version, "level": level, "mask": best_mask}


def save_png(grid, path, scale=12, border=4):
    from PIL import Image
    n = len(grid)
    size = (n + 2 * border) * scale
    img = Image.new("L", (size, size), 255)
    px = img.load()
    for r in range(n):
        for c in range(n):
            if grid[r][c]:
                for dy in range(scale):
                    for dx in range(scale):
                        px[(c + border) * scale + dx, (r + border) * scale + dy] = 0
    img.save(path)
