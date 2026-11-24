"""Step 1 and 2: turn the message into numbers, then into bits, then into bytes.

A QR code can store text in different "modes". This tiny version supports two:

* alphanumeric: digits, CAPITAL letters, space and  $ % * + - . / :
  Every character gets a number from a fixed table (0-44), and characters
  are packed two at a time into 11 bits.
* byte: anything else, one byte (8 bits) per character.
"""

ALPHANUMERIC_TABLE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"

# Codewords for versions 1-4:
# (version, level) -> (number of blocks, data codewords per block, error-correction codewords per block)
CAPACITY = {
    (1, "L"): (1, 19, 7),  (1, "M"): (1, 16, 10), (1, "Q"): (1, 13, 13), (1, "H"): (1, 9, 17),
    (2, "L"): (1, 34, 10), (2, "M"): (1, 28, 16), (2, "Q"): (1, 22, 22), (2, "H"): (1, 16, 28),
    (3, "L"): (1, 55, 15), (3, "M"): (1, 44, 26), (3, "Q"): (2, 17, 18), (3, "H"): (2, 13, 22),
    (4, "L"): (1, 80, 20), (4, "M"): (2, 32, 18), (4, "Q"): (2, 24, 26), (4, "H"): (4, 9, 16),
}

MODE_BITS = {"alphanumeric": "0010", "byte": "0100"}
COUNT_BITS = {"alphanumeric": 9, "byte": 8}  # length of the character-count label (versions 1-9)


def pick_mode(message):
    if all(ch in ALPHANUMERIC_TABLE for ch in message):
        return "alphanumeric"
    return "byte"


def letters_to_numbers(message):
    """M -> 22, A -> 10, T -> 29, space -> 36, ..."""
    return [ALPHANUMERIC_TABLE.index(ch) for ch in message]


def message_bits(message, mode):
    """The message as a string of 0s and 1s (without the header)."""
    bits = ""
    if mode == "alphanumeric":
        nums = letters_to_numbers(message)
        for i in range(0, len(nums) - 1, 2):
            bits += format(nums[i] * 45 + nums[i + 1], "011b")  # two letters -> 11 bits
        if len(nums) % 2 == 1:
            bits += format(nums[-1], "06b")  # a leftover letter -> 6 bits
    else:
        for b in message.encode("utf-8"):
            bits += format(b, "08b")
    return bits


def data_bits_needed(message, mode):
    return 4 + COUNT_BITS[mode] + len(message_bits(message, mode))


def choose_version(message, mode, level):
    """The smallest version (1-4) whose data area fits the message."""
    for version in range(1, 5):
        blocks, data_per_block, _ = CAPACITY[(version, level)]
        if data_bits_needed(message, mode) <= blocks * data_per_block * 8:
            return version
    raise ValueError("Message too long for this tiny QR maker (versions 1-4 only).")


def data_codewords(message, mode, version, level):
    """Header + message + terminator + padding, cut into bytes."""
    blocks, data_per_block, _ = CAPACITY[(version, level)]
    capacity_bits = blocks * data_per_block * 8

    count = len(message) if mode == "alphanumeric" else len(message.encode("utf-8"))
    bits = MODE_BITS[mode] + format(count, f"0{COUNT_BITS[mode]}b") + message_bits(message, mode)

    bits += "0" * min(4, capacity_bits - len(bits))  # terminator
    bits += "0" * (-len(bits) % 8)                   # fill to a whole byte
    codewords = [int(bits[i:i + 8], 2) for i in range(0, len(bits), 8)]

    pad = [0xEC, 0x11]                               # the standard padding bytes, taking turns
    i = 0
    while len(codewords) < blocks * data_per_block:
        codewords.append(pad[i % 2])
        i += 1
    return codewords, bits
