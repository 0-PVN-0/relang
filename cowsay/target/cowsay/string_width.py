import unicodedata


def string_width(s):
    if s is None:
        return 0
    width = 0
    for ch in s:
        cp = ord(ch)
        if cp == 0:
            continue
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            width += 2
        elif unicodedata.east_asian_width(ch) == "A":
            width += 2 if _is_cjk(ch) else 1
        else:
            width += 1
    return width


def _is_cjk(ch):
    cp = ord(ch)
    return (
        (0x1100 <= cp <= 0x115F)
        or (0x2E80 <= cp <= 0x303E)
        or (0x3040 <= cp <= 0x33FF)
        or (0x3400 <= cp <= 0x4DBF)
        or (0x4E00 <= cp <= 0x9FFF)
        or (0xA000 <= cp <= 0xA4CF)
        or (0xAC00 <= cp <= 0xD7AF)
        or (0xF900 <= cp <= 0xFAFF)
        or (0xFE30 <= cp <= 0xFE4F)
        or (0xFF01 <= cp <= 0xFF60)
        or (0xFFE0 <= cp <= 0xFFE6)
    )
