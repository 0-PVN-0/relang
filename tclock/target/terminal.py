"""Terminal control: ANSI sequences, raw mode, mouse, screen, colors."""

import os
import sys
import struct
import time

from color import RGB, RESET as COLOR_RESET, from_string, to_rgb

# ANSI escape sequence helpers
_ESC = "\033"
_CSI = f"{_ESC}["

# Box drawing characters
_HALF_BLOCK_UPPER = "\u2580"
_HALF_BLOCK_LOWER = "\u2584"
_FULL_BLOCK = "\u2588"
FULL_PIXEL = _FULL_BLOCK
BOTTOM_HALF_PIXEL = _HALF_BLOCK_LOWER

TRUE_COLOR_DISC_DEFAULT = "E0C020"
NOTRUE_COLOR_DISC_DEFAULT = "FFFFFF"

COLOR_HELP = (
    "none, black, red, green, yellow, orange, blue, purple, cyan, gray, "
    "darkgray, brightred, brightgreen, brightyellow, brightblue, "
    "brightpurple, brightcyan, white"
)


def _emit(s, out=None):
    if out is None:
        out = sys.stdout.buffer
    if isinstance(s, str):
        s = s.encode("utf-8")
    out.write(s)


def _emitf(out, fmt, *args):
    _emit(fmt.format(*args) if args else fmt, out)


def detect_color_mode():
    """Detect if true color is supported."""
    colorterm = os.environ.get("COLORTERM", "")
    return colorterm in ("truecolor", "24bit")


class AnsiPixels:
    def __init__(self, fps=30):
        self.W = 80
        self.H = 24
        self.Mx = -1
        self.My = -1
        self.TrueColor = detect_color_mode()
        self.Background = RGB(0, 0, 0)
        self.Out = sys.stdout.buffer
        self.Data = b""
        self._mouse_press = False
        self._mouse_release = False
        self._mouse_x = -1
        self._mouse_y = -1
        self._raw_mode = False
        self._cursor_saved = False
        self._sync_active = False
        self._prev_buf = b""
        self._mouse_tracking = False
        self.OnResize = None
        self._frame_time = 1.0 / fps if fps > 0 else 1.0 / 30
        self._color_output_initialized = False
        self._fg_color = None
        self._bg_color = None

    # --- Color output ---
    @property
    def ColorOutput(self):
        return self

    def Foreground(self, color):
        if isinstance(color, tuple):
            color = RGB(*color)
        if self.TrueColor:
            return color.foreground()
        else:
            idx = color.to_256()
            return f"{_CSI}38;5;{idx}m"

    def BackgroundStr(self, color):
        if isinstance(color, tuple):
            color = RGB(*color)
        if self.TrueColor:
            return color.background()
        else:
            idx = color.to_256()
            return f"{_CSI}48;5;{idx}m"

    # --- Terminal setup ---
    def Open(self):
        if sys.platform == "win32":
            self._enable_win32_console()
        self.GetSize()

    def Close(self):
        self.ShowCursor()
        self.MouseTrackingOff()
        self.EndSyncMode()
        self._restore_terminal()

    def _enable_win32_console(self):
        """Enable virtual terminal processing on Windows."""
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            STD_OUTPUT_HANDLE = -11
            STD_INPUT_HANDLE = -10
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            ENABLE_EXTENDED_FLAGS = 0x0080
            DISABLE_NEWLINE_AUTO_RETURN = 0x0008

            h_out = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            out_mode = ctypes.c_uint32()
            kernel32.GetConsoleMode(h_out, ctypes.byref(out_mode))
            out_mode.value |= (ENABLE_VIRTUAL_TERMINAL_PROCESSING | ENABLE_EXTENDED_FLAGS)
            out_mode.value &= ~DISABLE_NEWLINE_AUTO_RETURN
            kernel32.SetConsoleMode(h_out, out_mode)

            h_in = kernel32.GetStdHandle(STD_INPUT_HANDLE)
            in_mode = ctypes.c_uint32()
            kernel32.GetConsoleMode(h_in, ctypes.byref(in_mode))
            self._old_console_mode = in_mode.value
            ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
            in_mode.value |= (ENABLE_VIRTUAL_TERMINAL_INPUT | 0x0001)
            in_mode.value &= ~(0x0004 | 0x0002 | 0x0010)
            kernel32.SetConsoleMode(h_in, in_mode)
            self._raw_mode = True
        except Exception:
            pass

    def _restore_terminal(self):
        if sys.platform == "win32" and hasattr(self, "_old_console_mode"):
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                h_in = kernel32.GetStdHandle(-10)
                kernel32.SetConsoleMode(h_in, self._old_console_mode)
            except Exception:
                pass

    def GetSize(self):
        try:
            import shutil
            sz = shutil.get_terminal_size()
            self.W = sz.columns
            self.H = sz.lines
        except Exception:
            self.W = 80
            self.H = 24
        return self.W, self.H

    def SyncBackgroundColor(self):
        pass

    # --- Cursor ---
    def HideCursor(self):
        _emit(f"{_CSI}?25l", self.Out)
        self._flush()

    def ShowCursor(self):
        _emit(f"{_CSI}?25h", self.Out)
        self._flush()

    def MoveCursor(self, x, y):
        y = max(0, y)
        x = max(0, x)
        _emit(f"{_CSI}{y + 1};{x + 1}H", self.Out)

    def WriteAt(self, x, y, fmt, *args):
        self.MoveCursor(x, y)
        s = fmt.format(*args) if args else fmt
        _emit(s.encode("utf-8"), self.Out)

    def WriteAtStr(self, x, y, s):
        self.MoveCursor(x, y)
        _emit(s.encode("utf-8"), self.Out)

    def WriteString(self, s):
        _emit(s.encode("utf-8"), self.Out)

    def WriteRune(self, r):
        _emit(r.encode("utf-8") if isinstance(r, str) else r, self.Out)

    # --- Mouse ---
    def MouseTrackingOn(self):
        _emit(f"{_CSI}?1000h", self.Out)
        _emit(f"{_CSI}?1006h", self.Out)
        self._flush()
        self._mouse_tracking = True

    def MouseTrackingOff(self):
        _emit(f"{_CSI}?1006l", self.Out)
        _emit(f"{_CSI}?1000l", self.Out)
        self._flush()
        self._mouse_tracking = False

    def LeftClick(self):
        return self._mouse_press

    def MouseRelease(self):
        return self._mouse_release

    # --- Screen ---
    def ClearScreen(self):
        _emit(f"{_CSI}2J{_CSI}H", self.Out)
        self._flush()

    def StartSyncMode(self):
        if not self._sync_active:
            _emit(f"{_CSI}?2026h", self.Out)
            self._sync_active = True

    def EndSyncMode(self):
        if self._sync_active:
            _emit(f"{_CSI}?2026l", self.Out)
            self._sync_active = False
        self._flush()

    def SaveCursorPos(self):
        _emit(f"{_CSI}s", self.Out)
        self._cursor_saved = True

    def RestoreCursorPos(self):
        _emit(f"{_CSI}u", self.Out)
        self._flush()

    # --- Box drawing ---
    def DrawRoundBox(self, x, y, w, h):
        tl = "\u256d"
        tr = "\u256e"
        bl = "\u2570"
        br = "\u256f"
        hz = "\u2500"
        vt = "\u2502"
        self.WriteAt(x, y, tl + hz * (w - 2) + tr)
        for i in range(1, h - 1):
            self.WriteAt(x, y + i, vt + " " * (w - 2) + vt)
        self.WriteAt(x, y + h - 1, bl + hz * (w - 2) + br)

    def DrawColoredBox(self, x, y, w, h, color_str, _):
        try:
            c, _ = from_string(color_str)
        except Exception:
            c = None
        if c:
            self.WriteString(c.foreground())
        tl = "\u250c"
        tr = "\u2510"
        bl = "\u2514"
        br = "\u2518"
        hz = "\u2500"
        vt = "\u2502"
        self.WriteAt(x, y, tl + hz * (w - 2) + tr)
        for i in range(1, h - 1):
            self.WriteAt(x, y + i, vt + " " * (w - 2) + vt)
        self.WriteAt(x, y + h - 1, bl + hz * (w - 2) + br)
        if c:
            self.WriteString(COLOR_RESET)

    def DrawSquareBox(self, x, y, w, h):
        tl = "\u250c"
        tr = "\u2510"
        bl = "\u2514"
        br = "\u2518"
        hz = "\u2500"
        vt = "\u2502"
        self.WriteAt(x, y, tl + hz * (w - 2) + tr)
        for i in range(1, h - 1):
            self.WriteAt(x, y + i, vt + " " * (w - 2) + vt)
        self.WriteAt(x, y + h - 1, bl + hz * (w - 2) + br)

    # --- Disc ---
    def DiscBlendFN(self, cx, cy, radius, bg, fg, aliasing, blend_fn):
        for dy in range(-radius, radius + 1):
            y = cy + dy
            if y < 0 or y >= self.H:
                continue
            for dx in range(-radius, radius + 1):
                x = cx + dx
                if x < 0 or x >= self.W:
                    continue
                dist = (dx * dx + dy * dy) ** 0.5
                if dist <= radius:
                    alpha = 1.0
                    if aliasing > 0 and dist > radius - aliasing:
                        alpha = max(0.0, (radius - dist) / aliasing)
                        if alpha >= 1.0:
                            alpha = 1.0
                    if alpha <= 0:
                        continue
                    blended = blend_fn(bg, fg, alpha)
                    self.WriteAt(x, y, self.Foreground(blended) + "\u2588" + COLOR_RESET)

    # --- Input ---
    def ReadOrResizeOrSignalOnce(self):
        """Read and process one input event. Returns True if something happened."""
        self._mouse_press = False
        self._mouse_release = False
        self.Data = b""

        got_anything = False
        in_data = self._read_input(timeout=self._frame_time)

        if in_data:
            self.Data = in_data
            self._parse_mouse(in_data)
            got_anything = True

        new_w, new_h = self.GetSize()
        if new_w != self.W or new_h != self.H:
            self.W = new_w
            self.H = new_h
            if self.OnResize:
                try:
                    self.OnResize()
                except Exception:
                    pass
            got_anything = True

        return got_anything

    def _read_input(self, timeout=0.033):
        """Read available input with timeout."""
        data = b""
        if sys.platform == "win32":
            import msvcrt
            end = time.time() + timeout
            while time.time() < end:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    data += ch.encode("utf-8")
                    if ch == '\n' or ch == '\r':
                        break
                else:
                    time.sleep(0.001)
        else:
            import select
            while True:
                r, _, _ = select.select([sys.stdin], [], [], timeout)
                if r:
                    ch = sys.stdin.buffer.read(1)
                    if not ch:
                        break
                    data += ch
                else:
                    break
        return data

    def _parse_mouse(self, data):
        """Parse SGR mouse sequences."""
        s = data.decode("utf-8", errors="replace")
        idx = s.find(f"{_ESC}[<")
        if idx < 0:
            return
        remaining = s[idx + 3:]
        parts = remaining.split(";")
        if len(parts) >= 3:
            try:
                btn = int(parts[0])
                col = int(parts[1])
                row = int(parts[2].rstrip("Mm"))
                self._mouse_x = col - 1
                self._mouse_y = row - 1
                self.Mx = self._mouse_x
                self.My = self._mouse_y
                term = parts[2][-1] if parts[2] else "M"
                if term == "m":
                    self._mouse_release = True
                elif btn == 0:
                    self._mouse_press = True
            except (ValueError, IndexError):
                pass

    # --- Helpers ---
    def ScreenWidth(self, s):
        return len(s)

    def _flush(self):
        try:
            self.Out.flush()
        except Exception:
            pass


def BlendLinear(bg, fg, alpha):
    r = int(bg.r + (fg.r - bg.r) * alpha)
    g = int(bg.g + (fg.g - bg.g) * alpha)
    b = int(bg.b + (fg.b - bg.b) * alpha)
    return RGB(min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))


def BlendNSRGB(bg, fg, alpha):
    return BlendLinear(bg, fg, alpha)


def DrawAALine(img, x1, y1, x2, y2, color):
    """Anti-aliased line drawing using Wu's algorithm, operating on a list-of-lists pixel buffer."""
    w = len(img[0])
    h = len(img)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        ix = int(round(x1))
        iy = int(round(y1))
        if 0 <= ix < w and 0 <= iy < h:
            img[iy][ix] = color
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy


def ShowScaledImage(ap, img):
    """Render a 2D pixel buffer to terminal using half blocks."""
    w = len(img[0])
    h = len(img)
    out_h = h // 2
    for y in range(out_h):
        for x in range(w):
            top = img[y * 2][x]
            bot = img[y * 2 + 1][x] if y * 2 + 1 < h else RGB(0, 0, 0)
            if top == bot:
                ap.WriteString(ap.Foreground(top) + FULL_PIXEL + COLOR_RESET)
            elif top.r == 0 and top.g == 0 and top.b == 0:
                ap.WriteString(ap.Foreground(bot) + BOTTOM_HALF_PIXEL + COLOR_RESET)
            elif bot.r == 0 and bot.g == 0 and bot.b == 0:
                ap.WriteString(ap.Foreground(top) + _HALF_BLOCK_UPPER + COLOR_RESET)
            else:
                ap.WriteString(ap.Foreground(top))
                ap.WriteString(ap.BackgroundStr(bot))
                ap.WriteString(_HALF_BLOCK_LOWER + COLOR_RESET)
        ap.WriteString("\r\n")
