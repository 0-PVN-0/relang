"""tclock — Terminal Clock. Main entry point."""

import argparse
import io
import os
import signal
import sys
import time
from datetime import datetime, timedelta

import bignum
import duration
from analog import draw_hands, draw_image
from color import RGB, INVERSE, from_string, to_rgb
from terminal import (
    AnsiPixels, BlendLinear, BlendNSRGB,
    TRUE_COLOR_DISC_DEFAULT, NOTRUE_COLOR_DISC_DEFAULT,
    COLOR_RESET, COLOR_HELP,
)


class Config:
    def __init__(self):
        self.ap = None
        self.boxed = False
        self.color = ""
        self.color_box = ""
        self.analog = False
        self.inverse = False
        self.debug = False
        self.bounce = 0
        self.bounce_speed = 0
        self.frame = 0
        self.breath = False
        self.bcolor = RGB(0, 0, 0)
        self.color_output = None
        self.color_disc = None
        self.radius = 1.2
        self.fill_black = False
        self.aliasing = 0.8
        self.black_bg = ""
        self.blending_function = BlendNSRGB
        self.text = ""
        self.top_right = False
        self.tail = None
        self.count_down = False
        self.end = None
        self.extra_new_lines_at_end = True
        self.format = "03:%M"  # Go "3:04" maps to "3:04" in strftime... actually "%-I:%M"
        self.track_mouse = False
        self.blink_enabled = True
        self.seconds = True
        self.now = None
        self.aa = False
        self.continuous = False
        self._is_24h = False


def bounce_value(frame, maximum):
    m = frame % (2 * maximum)
    if m < maximum:
        return m
    return 2 * maximum - 1 - m


def time_string(num_str, blink):
    return bignum.time_string(num_str, blink)


def rgb_color(color):
    if isinstance(color, RGB):
        return color
    c, _ = from_string(str(color))
    return c


def duration_string_fn(dur, with_seconds):
    return duration.duration_string(dur, with_seconds)


def format_time(cfg, t):
    s = t.strftime(cfg.format)
    if not cfg._is_24h and s.startswith("0"):
        s = s[1:]
    return s


def main():
    sys.exit(main_func())


def main_func():
    truecolor_default = os.environ.get("COLORTERM", "") in ("truecolor", "24bit")
    disc_default = TRUE_COLOR_DISC_DEFAULT if truecolor_default else NOTRUE_COLOR_DISC_DEFAULT

    parser = argparse.ArgumentParser(
        description="Terminal Clock",
        usage="%(prog)s [flags] [digits... or - for stdin tailing]",
    )
    parser.add_argument("digits", nargs="?", default=None,
                        help="digits to display as big numbers, or '-' for stdin tail")
    parser.add_argument("-bounce", type=int, default=0, help="Bounce speed (0 = no bounce)")
    parser.add_argument("-24", action="store_true", help="Use 24-hour time format")
    parser.add_argument("-analog", action="store_true", help="Analog clock")
    parser.add_argument("-no-seconds", action="store_true", help="Don't show seconds")
    parser.add_argument("-no-blink", action="store_true", help="Don't blink the colon")
    parser.add_argument("-box", action="store_true", help="Draw box around the time")
    parser.add_argument("-color-disc", default=disc_default, help="Color disc around the time")
    parser.add_argument("-radius", type=float, default=1.2, help="Radius of disc (proportion of width)")
    parser.add_argument("-black-bg", action="store_true", help="Black background")
    parser.add_argument("-aliasing", type=float, default=0.8, help="Aliasing factor for disc")
    parser.add_argument("-color-box", default="", help="Color box around the time")
    parser.add_argument("-color", default="red", help=f"Color to use: RRGGBB, hue,sat,lum or named color ({COLOR_HELP})")
    parser.add_argument("-breath", action="store_true", help="Pulse the color")
    parser.add_argument("-inverse", action="store_true", help="Inverse foreground/background")
    parser.add_argument("-debug", action="store_true", help="Debug mode")
    parser.add_argument("-truecolor", default=truecolor_default, action="store_true",
                        help="Use true color (24-bit RGB)")
    parser.add_argument("-no-truecolor", dest="truecolor", action="store_false",
                        help="Disable true color")
    parser.add_argument("-linear", action="store_true", help="Use linear blending for disc")
    parser.add_argument("-countdown", default="0", help="Countdown duration (e.g. 5m, 3w2d10h)")
    parser.add_argument("-text", default="", help="Text to display below the clock")
    parser.add_argument("-until", default="", help="Countdown until date/time")
    parser.add_argument("-tail", default="", help="Tail filename ('-' for stdin)")
    parser.add_argument("-aa", action="store_true", help="Anti-aliased analog clock")
    parser.add_argument("-c", action="store_true", help="Continuous analog updates")
    parser.add_argument("-fps", type=float, default=30, help="Max frames per second")

    args = parser.parse_args()

    is_24 = getattr(args, "24")
    format_str = "%H:%M" if is_24 else "%I:%M"

    cfg = Config()
    cfg.boxed = args.box
    cfg.inverse = args.inverse
    cfg.debug = args.debug
    cfg.breath = args.breath
    cfg.radius = args.radius
    cfg.fill_black = args.black_bg
    cfg.aliasing = args.aliasing
    cfg.format = format_str
    cfg.seconds = not args.no_seconds
    cfg.bounce_speed = args.bounce
    cfg.blink_enabled = not args.no_blink
    cfg.extra_new_lines_at_end = True
    cfg.analog = args.analog
    cfg.aa = args.aa
    cfg.continuous = getattr(args, "c")

    if cfg.continuous and not cfg.analog and not cfg.aa:
        cfg.aa = True

    ap = AnsiPixels(args.fps)
    ap.TrueColor = args.truecolor
    cfg.ap = ap

    color_disc = args.color_disc
    if ap.TrueColor != truecolor_default and color_disc == disc_default:
        color_disc = TRUE_COLOR_DISC_DEFAULT if ap.TrueColor else NOTRUE_COLOR_DISC_DEFAULT

    if cfg.seconds:
        cfg.format += ":%S"

    show_text = args.text != "none"
    if show_text:
        cfg.text = args.text

    cfg.now = datetime.now()

    if args.countdown != "0":
        cfg.count_down = True
        try:
            cd = duration.parse_duration(args.countdown)
        except ValueError as e:
            print(f"Invalid countdown duration: {e}", file=sys.stderr)
            return 1
        cfg.end = cfg.now + cd

    if args.until:
        cfg.count_down = True
        try:
            cfg.end = duration.parse_datetime(cfg.now, args.until)
        except ValueError as e:
            print(f"Invalid until time: {e}", file=sys.stderr)
            return 1

    if cfg.count_down and show_text and cfg.text == "":
        end_str = format_time(cfg, cfg.end)
        if (cfg.end - cfg.now).total_seconds() >= 86400:
            end_str = f"{cfg.end.strftime('%Y-%m-%d')} {end_str}"
        extra = ""
        if not is_24 and cfg.end.hour >= 12:
            extra = " pm"
        cfg.text = "Countdown to " + end_str + extra

    if args.linear:
        cfg.blending_function = BlendLinear
    else:
        cfg.blending_function = BlendNSRGB

    try:
        parsed_color, _ = from_string(args.color)
    except ValueError as e:
        print(f"Color error: {e}", file=sys.stderr)
        return 1

    if cfg.breath:
        cfg.bcolor = to_rgb(parsed_color)
    else:
        cfg.color = ap.Foreground(parsed_color)

    if args.color_box:
        try:
            cb, _ = from_string(args.color_box)
        except ValueError as e:
            print(f"Color box error: {e}", file=sys.stderr)
            return 1
        cfg.color_box = ap.Foreground(cb)
        cfg.boxed = True

    if color_disc:
        try:
            cd, _ = from_string(color_disc)
        except ValueError as e:
            print(f"Color disc error: {e}", file=sys.stderr)
            return 1
        cfg.color_disc = to_rgb(cd)

    ap.GetSize()
    if ap.TrueColor:
        cfg.black_bg = RGB(0, 0, 0).background()
    else:
        cfg.black_bg = "\033[40m"

    ap.Background = RGB(0, 0, 0)

    # Handle positional argument
    if args.digits is not None:
        num_str = args.digits
        if num_str == "-":
            return stdin_tail(cfg.tail_mode())
        if len(num_str) == 0 or not num_str[0].isdigit():
            print("No arguments, or <digits> or -", file=sys.stderr)
            return 1
        sys.stdout.buffer.write(time_string(num_str, False).encode("utf-8") + b"\n")
        sys.stdout.buffer.flush()
        return 0

    if args.tail:
        cfg.tail_mode()
        if args.tail == "-":
            return stdin_tail(cfg)
        try:
            f = open(args.tail, "rb")
        except OSError as e:
            print(f"Error opening tail file: {e}", file=sys.stderr)
            return 1
        cfg.tail = f
        ap.SaveCursorPos()
        cfg.extra_new_lines_at_end = False

    ap.Open()

    if not cfg.top_right:
        ap.HideCursor()
        if not cfg.fill_black:
            ap.SyncBackgroundColor()
        cfg.clear_screen()

    if cfg.bounce_speed <= 0 and not cfg.top_right and not cfg.analog:
        ap.MouseTrackingOn()
        cfg.track_mouse = True

    return raw_mode_loop(cfg)


def raw_mode_loop(cfg):
    ap = cfg.ap
    num_str = ""
    blink = False
    prev_now = None
    x, y = ap.Mx, ap.My
    frame = 0
    prev = ""

    def on_resize():
        cfg.clear_screen()
        cfg.ap.StartSyncMode()
        cfg.draw_at(-1, -1, time_string(prev, False))
        cfg.ap.EndSyncMode()
    ap.OnResize = on_resize

    while True:
        ap.ReadOrResizeOrSignalOnce()
        do_draw = cfg.breath or cfg.continuous

        if len(ap.Data) > 0:
            first_byte = ap.Data[0:1]
            if sys.platform == "win32":
                first_ch = ap.Data.decode("utf-8", errors="replace")[:1]
            else:
                first_ch = ap.Data[:1].decode("utf-8", errors="replace")
            if first_ch in ("q", "\x03"):
                if cfg.count_down:
                    ap.WriteAt(0, ap.H - 3, f"Countdown aborted at {format_time(cfg, cfg.now)}\r\n")
                    return 1
                return 0
            if first_ch in ("a", "A"):
                cfg.aa = not cfg.aa
                cfg.analog = not cfg.aa
                do_draw = True
            if first_ch in ("c", "C"):
                cfg.continuous = not cfg.continuous
                do_draw = True

        if ap.LeftClick() and ap.MouseRelease():
            cfg.track_mouse = not cfg.track_mouse

        cfg.now = datetime.now()

        if cfg.count_down:
            left = cfg.end - cfg.now
            if left.total_seconds() < 0:
                ap.WriteAt(0, ap.H - 2, f"\aTime's up reached at {format_time(cfg, cfg.now)}\r\n")
                cfg.extra_new_lines_at_end = False
                return 0
            num_str = duration_string_fn(left, cfg.seconds)
        else:
            num_str = format_time(cfg, cfg.now)

        if num_str != prev:
            do_draw = True
        prev = num_str

        if not cfg.continuous:
            cfg.now = cfg.now.replace(microsecond=0)

        if cfg.now != prev_now and cfg.blink_enabled:
            blink = not blink
            do_draw = True
        prev_now = cfg.now

        if cfg.bounce_speed > 0:
            if frame % cfg.bounce_speed == 0:
                cfg.bounce += 1
                do_draw = True
            frame += 1
        elif cfg.track_mouse and (ap.Mx != x or ap.My != y):
            x, y = ap.Mx, ap.My
            do_draw = True

        tail_bytes = b""
        if cfg.tail is not None:
            try:
                tail_bytes = cfg.tail.read(4096)
                if tail_bytes is None:
                    tail_bytes = b""
            except Exception:
                tail_bytes = b""

        if do_draw or len(tail_bytes) > 0:
            cfg.frame += 1
            ap.StartSyncMode()
            if cfg.tail is None:
                cfg.clear_screen()
            if len(tail_bytes) > 0:
                ap.Out.write(tail_bytes)
                ap.SaveCursorPos()
            cfg.draw_at(x - 1, y - 1, time_string(num_str, blink))
            ap.RestoreCursorPos()
            ap.EndSyncMode()


def stdin_tail(cfg):
    max_poll = 0.1  # 100ms
    num_str = ""
    ap = cfg.ap
    blink = False
    prev_now = None
    prev = ""

    class TimeoutStdinReader:
        def __init__(self, timeout):
            self._timeout = timeout

        def read(self, size):
            import msvcrt
            end = time.time() + self._timeout
            data = b""
            while time.time() < end:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch == '\r':
                        data += b'\n'
                        break
                    data += ch.encode("utf-8")
                    if len(data) >= size:
                        break
                else:
                    time.sleep(0.001)
            return data

    # On Windows, read is blocking originally, need to use msvcrt
    if sys.platform == "win32":
        reader = TimeoutStdinReader(max_poll)
    else:
        import select
        class UnixReader:
            def __init__(self, timeout):
                self._timeout = timeout
            def read(self, size):
                r, _, _ = select.select([sys.stdin], [], [], self._timeout)
                if r:
                    return sys.stdin.buffer.read(size)
                return b""
        reader = UnixReader(max_poll)

    in_reader = io.BufferedReader(io.FileIO(sys.stdin.fileno(), "rb"))
    out_writer = io.BufferedWriter(io.FileIO(sys.stdout.fileno(), "wb"))
    ap.Out = out_writer

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

    while True:
        do_draw = cfg.breath
        now = datetime.now()
        if cfg.count_down:
            left = cfg.end - now
            if left.total_seconds() < 0:
                ap.WriteString(f"\n\n\aTime's up reached at {now.strftime(cfg.format)}\r\n")
                return 0
            num_str = duration_string_fn(left, cfg.seconds)
        else:
            num_str = now.strftime(cfg.format)
        if num_str != prev:
            do_draw = True
        prev = num_str
        now = now.replace(microsecond=0)
        if now != prev_now and cfg.blink_enabled:
            blink = not blink
            do_draw = True
        prev_now = now

        tail_bytes = reader.read(4096) if hasattr(reader, 'read') else b""

        if do_draw or len(tail_bytes) > 0:
            cfg.frame += 1
            ap.StartSyncMode()
            if len(tail_bytes) > 0:
                ap.Out.write(tail_bytes)
                ap.SaveCursorPos()
            cfg.draw_at(-1, -1, time_string(num_str, blink))
            ap.RestoreCursorPos()
            ap.EndSyncMode()


Config.tail_mode = lambda self: setattr(self, 'top_right', True) or setattr(self, 'color_disc', None) or setattr(self, 'boxed', True) or self

Config.clear_screen = lambda self: (
    self.ap.WriteString(self.black_bg) if self.fill_black else None,
    self.ap.ClearScreen()
) or None


def draw_at(cfg, x, y, str_text):
    ap = cfg.ap
    if cfg.aa:
        draw_image(cfg, cfg.now, cfg.seconds)
        return
    if cfg.analog:
        radius = min(ap.W // 2, ap.H) - 1
        draw_hands(cfg, ap.W // 2, ap.H // 2, radius, ap.Background, cfg.now, cfg.seconds)
        return
    if cfg.debug:
        ap.DrawSquareBox(0, 0, ap.W, ap.H)
        ap.WriteAt(0, ap.H - 1, f"Mouse {ap.Mx}, {ap.My} [{ap.W}x{ap.H}]")
    lines = str_text.split("\n")
    width = ap.ScreenWidth(lines[0]) if lines else 0
    if cfg.boxed:
        width += 2
    height = len(lines)
    if cfg.boxed:
        height += 2
    if (x < 0 and y < 0) or cfg.analog:
        x = ap.W // 2 - width // 2
        y = ap.H // 2 - height // 2
    if cfg.top_right:
        x = ap.W - width
        y = height - 1
    x = min(x, ap.W - 1)
    y = min(y, ap.H - 1)
    if cfg.bounce != 0:
        x = width - 1 + bounce_value(cfg.bounce, ap.W - width + 1)
        y = height - 1 + bounce_value(cfg.bounce, ap.H - height + 1)
    x += 1
    y += 1
    x = max(x, width)
    y = max(y, height)
    if cfg.color_disc is not None:
        mult = cfg.radius
        if cfg.breath:
            mult *= (1 + bounce_value(cfg.frame // 7, 10) / 15.0)
        radius = 2 * int(round(mult * width / 4.0))
        if radius <= height:
            radius = (2 * (height + 1)) // 2
        cx = x - width // 2 - 1
        cy = y - height // 2 - 1
        ap.DiscBlendFN(cx, cy, radius, ap.Background, cfg.color_disc, cfg.aliasing, cfg.blending_function)
    if cfg.boxed:
        if cfg.color_box:
            ap.DrawColoredBox(x - width, y - height, width, height, cfg.color_box, False)
        else:
            ap.DrawRoundBox(x - width, y - height, width, height)
        x -= 1
        y -= 1
        width -= 2
        height -= 2
    prefix = cfg.color
    if cfg.breath:
        prefix = ap.Foreground(cfg.breath_color())
    if cfg.inverse:
        prefix = INVERSE + cfg.color
    suffix = ""
    if cfg.fill_black:
        prefix += cfg.black_bg
    else:
        suffix = COLOR_RESET
    for i, line in enumerate(lines):
        ap.WriteAtStr(x - width, y - height + i, prefix + line + suffix)
    if cfg.text:
        center = x - width // 2 - ap.ScreenWidth(cfg.text) // 2 - 1
        ap.WriteAtStr(center, y + 1, cfg.text)


Config.draw_at = draw_at


def breath_color(cfg):
    spread = 100
    alpha = 0.15 + 0.85 * bounce_value(cfg.frame, spread) / spread
    return cfg.blending_function(cfg.ap.Background, cfg.bcolor, alpha).foreground()


Config.breath_color = breath_color


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()
