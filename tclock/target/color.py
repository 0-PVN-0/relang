"""Color parsing and ANSI escape sequence generation."""

import colorsys
import re

NAMED_COLORS = {
    "none": (0, 0, 0),
    "black": (0, 0, 0),
    "red": (255, 20, 30),
    "green": (20, 255, 30),
    "yellow": (255, 255, 20),
    "orange": (255, 165, 0),
    "blue": (30, 80, 255),
    "purple": (160, 30, 255),
    "cyan": (0, 255, 255),
    "gray": (128, 128, 128),
    "darkgray": (64, 64, 64),
    "brightred": (255, 100, 100),
    "brightgreen": (100, 255, 100),
    "brightyellow": (255, 255, 100),
    "brightblue": (100, 100, 255),
    "brightpurple": (200, 100, 255),
    "brightcyan": (100, 255, 255),
    "white": (255, 255, 255),
}


class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def __eq__(self, other):
        if isinstance(other, RGB):
            return (self.r, self.g, self.b) == (other.r, other.g, other.b)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.r, self.g, self.b))

    def __repr__(self):
        return f"RGB({self.r}, {self.g}, {self.b})"

    def foreground(self):
        return f"\033[38;2;{self.r};{self.g};{self.b}m"

    def background(self):
        return f"\033[48;2;{self.r};{self.g};{self.b}m"

    def to_color(self):
        return self

    def to_256(self):
        best = 0
        best_dist = float("inf")
        for idx, (cr, cg, cb) in _COLOR256_TABLE.items():
            dr = self.r - cr
            dg = self.g - cg
            db = self.b - cb
            d = dr * dr + dg * dg + db * db
            if d < best_dist:
                best_dist = d
                best = idx
        return best


_COLOR256_TABLE = {
    0: (0, 0, 0),
    1: (128, 0, 0),
    2: (0, 128, 0),
    3: (128, 128, 0),
    4: (0, 0, 128),
    5: (128, 0, 128),
    6: (0, 128, 128),
    7: (192, 192, 192),
    8: (128, 128, 128),
    9: (255, 0, 0),
    10: (0, 255, 0),
    11: (255, 255, 0),
    12: (0, 0, 255),
    13: (255, 0, 255),
    14: (0, 255, 255),
    15: (255, 255, 255),
}

for _r in range(6):
    for _g in range(6):
        for _b in range(6):
            idx = 16 + _r * 36 + _g * 6 + _b
            _COLOR256_TABLE[idx] = (_r * 51, _g * 51, _b * 51)

for _gray in range(24):
    idx = 232 + _gray
    v = 8 + _gray * 10
    _COLOR256_TABLE[idx] = (v, v, v)


RESET = "\033[0m"
INVERSE = "\033[7m"


def from_string(s):
    s = s.strip()
    if not s:
        return RGB(0, 0, 0), None

    # Named color
    if s.lower() in NAMED_COLORS:
        r, g, b = NAMED_COLORS[s.lower()]
        return RGB(r, g, b), None

    # Hex RRGGBB
    if re.match(r'^[0-9a-fA-F]{6}$', s):
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return RGB(r, g, b), None

    # HSL: hue,sat,lum
    m = re.match(r'^([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)$', s)
    if m:
        h = float(m.group(1))
        s_val = float(m.group(2))
        l_val = float(m.group(3))
        r, g, b = colorsys.hls_to_rgb(h, l_val, s_val)
        return RGB(int(r * 255), int(g * 255), int(b * 255)), None

    raise ValueError(f"unknown color: {s!r}")


def to_rgb(color):
    if isinstance(color, RGB):
        return color
    return from_string(str(color))[0]
