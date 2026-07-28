"""Analog clock hands and markers drawing for terminal output."""

import math
from color import RGB
from terminal import BOTTOM_HALF_PIXEL, FULL_PIXEL, COLOR_RESET


def calculate_angle(max_v, time_value):
    return 2.0 * math.pi * (max_v - time_value) / max_v


def rotate_from_12(theta, radius):
    return int(round(-math.sin(theta) * radius)), int(round(-math.cos(theta) * radius))


def angle_coords(max_v, time_value, radius):
    return rotate_from_12(calculate_angle(max_v, time_value), radius)


def bresenham_line(pix, sx, sy, x0i, y0i, color):
    """Bresenham line algorithm, with y doubled for half-block terminal pixels."""
    x1i = x0i + sx
    y0 = y0i * 2
    y1 = y0 + sy
    steep = abs(y1 - y0) > abs(x1i - x0i)
    if steep:
        x0i, y0 = y0, x0i
        x1i, y1 = y1, x1i
    if x0i > x1i:
        x0i, x1i = x1i, x0i
        y0, y1 = y1, y0
    dx = x1i - x0i
    dy = abs(y1 - y0)
    err = dx / 2.0
    y_step = 1 if y0 < y1 else -1
    y = y0
    for x in range(x0i, x1i + 1):
        if steep:
            pix[(y, x)] = color
        else:
            pix[(x, y)] = color
        err -= dy
        if err < 0:
            y += y_step
            err += dx


def draw_pixels(ap, pixels, background):
    """Render pixel map to terminal using half-block characters."""
    fg_color = None
    bg_color = None

    def set_colors(fg, bg):
        nonlocal fg_color, bg_color
        if fg_color != fg or bg_color != bg:
            fg_color = fg
            bg_color = bg
            if fg == bg:
                ap.WriteString(ap.Foreground(fg))
            else:
                ap.WriteString(ap.Foreground(fg))
                ap.WriteString(ap.BackgroundStr(bg))

    ordered = sorted(pixels.keys(), key=lambda p: (p[1], p[0]))
    for coord in ordered:
        color = pixels[coord]
        x, y = coord
        if y % 2 == 0:
            lower = (x, y + 1)
            ap.MoveCursor(x, y // 2)
            if lower in pixels:
                v = pixels[lower]
                if v == color:
                    set_colors(color, color)
                    ap.WriteRune(FULL_PIXEL)
                    continue
                set_colors(v, color)
                del pixels[lower]
            else:
                set_colors(background, color)
            ap.WriteRune(BOTTOM_HALF_PIXEL)
        else:
            upper = (x, y - 1)
            if upper not in pixels:
                ap.MoveCursor(x, y // 2)
                set_colors(color, background)
                ap.WriteRune(BOTTOM_HALF_PIXEL)
    ap.WriteString(COLOR_RESET)


def draw_hands(cfg, cx, cy, radius, background, now, seconds):
    """Draw analog clock hands and markers."""
    sec_val = float(now.second)
    minute_val = float(now.minute)
    hour_val = now.hour
    if cfg.continuous:
        sec_val = (now.microsecond / 1_000_000 + now.second) % 60
    r = float(radius)
    sx, sy = angle_coords(60, sec_val, 0.9 * r)
    m = minute_val + sec_val / 60.0
    mx, my = angle_coords(60, m, 0.80 * r)
    hx, hy = angle_coords(12, float(hour_val % 12) + m / 60.0, 0.47 * r)
    pix = {}
    if seconds:
        bresenham_line(pix, sx, sy, cx, cy, RGB(0x50, 0x80, 0x50))
    bresenham_line(pix, mx, my, cx, cy, RGB(0x2C, 0x59, 0xD4))
    bresenham_line(pix, hx, hy, cx, cy, RGB(255, 0xA7, 10))
    draw_pixels(cfg.ap, pix, background)
    cfg.ap.WriteString(COLOR_RESET)
    for n in range(1, 61):
        nx, ny = angle_coords(60, float(n % 60), r)
        if n % 5 == 0:
            marker = n // 5
            if marker >= 10:
                nx -= 1
            cfg.ap.WriteAt(cx + nx, cy + (ny - 1) // 2, str(marker))
        elif seconds:
            cfg.ap.WriteAt(cx + nx, cy + (ny - 1) // 2, "\u2022")


# --- Anti-aliased image-based analog ---

def point(a, r):
    return -r * math.sin(a), -r * math.cos(a)


def angle(max_v, time_value):
    return 2.0 * math.pi * (max_v - time_value) / max_v


def coords(max_v, time_value, radius):
    return point(angle(max_v, time_value), radius)


def draw_image(cfg, now, seconds):
    """Anti-aliased image-based analog clock drawing."""
    r = min(float(cfg.ap.W) / 2, float(cfg.ap.H)) - 1
    cxf = float(cfg.ap.W) / 2
    cyf = float(cfg.ap.H)
    cx = int(cxf)
    cy = int(cyf / 2)
    w = cfg.ap.W
    h = 2 * cfg.ap.H
    img = [[RGB(0, 0, 0) for _ in range(w)] for _ in range(h)]

    sec_val, minute_val, hour_val = float(now.second), float(now.minute), now.hour
    if cfg.continuous:
        sec_val = (now.microsecond / 1_000_000 + now.second) % 60

    sx, sy = coords(60, sec_val, 0.9 * r)
    m = minute_val + sec_val / 60.0
    mx, my = coords(60, m, 0.80 * r)
    hx, hy = coords(12, float(hour_val % 12) + m / 60.0, 0.47 * r)

    min_dot_color = RGB(255, 255, 255)
    hour_dot_color = RGB(255, 20, 20)
    if seconds:
        for n in range(60):
            c = min_dot_color if n % 5 != 0 else hour_dot_color
            nx1, ny1 = coords(60, float(n), r - 1.5)
            nx2, ny2 = coords(60, float(n), r + 0.5)
            _draw_aa_line(img, w, h, cxf + nx1, cyf + ny1, cxf + nx2, cyf + ny2, c)
        _draw_aa_line(img, w, h, cxf, cyf, cxf + sx, cyf + sy, RGB(0x50, 0x80, 0x50))
    _draw_aa_line(img, w, h, cxf, cyf, cxf + mx, cyf + my, RGB(0x2C, 0x59, 0xD4))
    _draw_aa_line(img, w, h, cxf, cyf, cxf + hx, cyf + hy, RGB(255, 0xA7, 10))

    _show_scaled_image(cfg.ap, img)

    if not seconds:
        cfg.ap.WriteString(COLOR_RESET)
        for n in range(5, 61, 5):
            nx, ny = angle_coords(60, float(n % 60), r)
            m_val = n // 5
            if m_val >= 10:
                nx -= 1
            cfg.ap.WriteAt(cx + nx, cy + (ny - 1) // 2, str(m_val))


def _draw_aa_line(img, w, h, x1, y1, x2, y2, color):
    """Simple anti-aliased line using Xiaolin Wu's algorithm."""
    def _fpart(x):
        return x - int(x)

    def _rfpart(x):
        return 1 - _fpart(x)

    def _blend(ix, iy, brightness):
        if 0 <= ix < w and 0 <= iy < h:
            existing = img[iy][ix]
            img[iy][ix] = RGB(
                min(255, existing.r + int((color.r - existing.r) * brightness)),
                min(255, existing.g + int((color.g - existing.g) * brightness)),
                min(255, existing.b + int((color.b - existing.b) * brightness)),
            )

    dx = x2 - x1
    dy = y2 - y1
    steep = abs(dy) > abs(dx)
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dx, dy = dy, dx
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        dx, dy = dy, dx

    grad = dy / dx if dx != 0 else 1.0
    xend = round(x1)
    yend = y1 + grad * (xend - x1)
    xgap = _rfpart(x1 + 0.5)
    xpxl1 = xend
    ypxl1 = int(yend)
    if steep:
        _blend(ypxl1, xpxl1, _rfpart(yend) * xgap)
        _blend(ypxl1 + 1, xpxl1, _fpart(yend) * xgap)
    else:
        _blend(xpxl1, ypxl1, _rfpart(yend) * xgap)
        _blend(xpxl1, ypxl1 + 1, _fpart(yend) * xgap)
    intery = yend + grad

    xend = round(x2)
    yend = y2 + grad * (xend - x2)
    xgap = _rfpart(x2 + 0.5)
    xpxl2 = xend
    ypxl2 = int(yend)
    if steep:
        _blend(ypxl2, xpxl2, _rfpart(yend) * xgap)
        _blend(ypxl2 + 1, xpxl2, _fpart(yend) * xgap)
    else:
        _blend(xpxl2, ypxl2, _rfpart(yend) * xgap)
        _blend(xpxl2, ypxl2 + 1, _fpart(yend) * xgap)

    if steep:
        for x in range(xpxl1 + 1, xpxl2):
            iy = int(intery)
            _blend(iy, x, _rfpart(intery))
            _blend(iy + 1, x, _fpart(intery))
            intery += grad
    else:
        for x in range(xpxl1 + 1, xpxl2):
            iy = int(intery)
            _blend(x, iy, _rfpart(intery))
            _blend(x, iy + 1, _fpart(intery))
            intery += grad


def _show_scaled_image(ap, img):
    """Render pixel buffer to terminal using half blocks."""
    w = len(img[0])
    h = len(img)
    out_h = h // 2
    prev_fg = None
    prev_bg = None

    def _set_colors(fg, bg):
        nonlocal prev_fg, prev_bg
        if prev_fg != fg:
            prev_fg = fg
            ap.WriteString(ap.Foreground(fg))
        if prev_bg != bg:
            prev_bg = bg
            ap.WriteString(ap.BackgroundStr(bg))

    for y in range(out_h):
        for x in range(w):
            top = img[y * 2][x]
            bot = img[y * 2 + 1][x] if y * 2 + 1 < h else RGB(0, 0, 0)
            if top == bot:
                _set_colors(top, top)
                ap.WriteRune(FULL_PIXEL)
            elif bot == RGB(0, 0, 0):
                _set_colors(top, top)
                ap.WriteRune("\u2580")
            elif top == RGB(0, 0, 0):
                _set_colors(bot, bot)
                ap.WriteRune(BOTTOM_HALF_PIXEL)
            else:
                _set_colors(top, bot)
                ap.WriteRune(BOTTOM_HALF_PIXEL)
        ap.WriteString("\r\n")
    ap.WriteString(COLOR_RESET)
