import argparse
import io
import qrcode
import sys

WHITE = "\033[47m  \033[0m"
BLACK = "\033[40m  \033[0m"

BLACK_WHITE = "▄"
BLACK_BLACK = " "
WHITE_BLACK = "▀"
WHITE_WHITE = "█"

QUIET_ZONE = 4

SIXEL_BEGIN = "\x1bPq\n#0;2;0;0;0#1;2;100;100;100\n"
SIXEL_END = "\x1b\\"
SIXEL_BLOCK_SIZE = 12


class Config:
    def __init__(self, level="H", writer=None, half_blocks=False,
                 black_char=BLACK, black_white_char=BLACK_WHITE,
                 white_char=WHITE, white_black_char=WHITE_BLACK,
                 quiet_zone=QUIET_ZONE, with_sixel=False):
        self.level = level
        self.writer = writer or sys.stdout
        self.half_blocks = half_blocks
        self.black_char = black_char
        self.black_white_char = black_white_char
        self.white_char = white_char
        self.white_black_char = white_black_char
        self.quiet_zone = quiet_zone
        self.with_sixel = with_sixel


def _get_qr_level(level):
    if level == "L":
        return qrcode.constants.ERROR_CORRECT_L
    if level == "M":
        return qrcode.constants.ERROR_CORRECT_M
    if level == "H":
        return qrcode.constants.ERROR_CORRECT_H
    return qrcode.constants.ERROR_CORRECT_H


def _encode(text, level):
    qr = qrcode.QRCode(border=0, error_correction=_get_qr_level(level), box_size=1)
    qr.add_data(text)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    size = len(matrix)
    return matrix, size


def _write_full_blocks(w, matrix, size, config):
    white = config.white_char
    black = config.black_char
    qz = config.quiet_zone

    w.write((white * (size + qz * 2) + "\n") * qz)

    for i in range(size):
        w.write(white * qz)
        for j in range(size):
            w.write(black if matrix[j][i] else white)
        w.write(white * (qz - 1) + "\n")

    w.write((white * (size + qz * 2) + "\n") * (qz - 1))


def _write_half_blocks(w, matrix, size, config):
    ww = config.white_char
    bb = config.black_char
    wb = config.white_black_char
    bw = config.black_white_char
    qz = config.quiet_zone

    if qz % 2 != 0:
        w.write(bw * (size + qz * 2) + "\n")
        w.write((ww * (size + qz * 2) + "\n") * (qz // 2))
    else:
        w.write((ww * (size + qz * 2) + "\n") * (qz // 2))

    for i in range(0, size, 2):
        w.write(ww * qz)
        for j in range(size):
            curr_black = matrix[j][i]
            next_black = matrix[j][i + 1] if i + 1 < size else False
            if curr_black and next_black:
                w.write(bb)
            elif curr_black and not next_black:
                w.write(bw)
            elif not curr_black and not next_black:
                w.write(ww)
            else:
                w.write(wb)
        w.write(ww * (qz - 1) + "\n")

    if qz % 2 == 0:
        w.write((ww * (size + qz * 2) + "\n") * (qz // 2 - 1))
        w.write(wb * (size + qz * 2) + "\n")
    else:
        w.write((ww * (size + qz * 2) + "\n") * (qz // 2))


def _write_sixel(w, matrix, size, config):
    block_size = SIXEL_BLOCK_SIZE
    if size > 50:
        block_size //= 2
    line = block_size // 6
    qz = config.quiet_zone

    w.write(SIXEL_BEGIN)

    w.write(("#1!{}~-\n".format(block_size * (size + qz * 2))) * (qz * line))

    for i in range(size):
        repeat = 0
        content_parts = []
        flag = -1
        if qz > 0:
            content_parts.append("#1!{}~".format(block_size * qz))
        for j in range(size):
            if matrix[j][i]:
                if flag == 1:
                    content_parts.append("#1!{}~".format(block_size * repeat))
                    repeat = 0
                flag = 0
                repeat += 1
            else:
                if flag == 0:
                    content_parts.append("#0!{}~".format(block_size * repeat))
                    repeat = 0
                flag = 1
                repeat += 1
        if repeat > 0:
            content_parts.append("#{}!{}~".format(flag, block_size * repeat))
        if qz > 1:
            content_parts.append("#1!{}~".format(block_size * (qz - 1)))
        content_parts.append("-\n")
        line_data = "".join(content_parts)
        for _ in range(line):
            w.write(line_data)

    w.write(("#1!{}~-\n".format(block_size * (size + qz * 2))) * ((qz - 1) * line))
    if qz > 1:
        w.write("#1!{}~-".format(block_size * (size + qz * 2)))

    w.write(SIXEL_END)


def generate_with_config(text, config):
    if config.quiet_zone < 1:
        config.quiet_zone = 1

    matrix, size = _encode(text, config.level)

    if config.black_char == "":
        config.black_char = BLACK_BLACK
    if config.white_black_char == "":
        config.white_black_char = WHITE_BLACK
    if config.white_char == "":
        config.white_char = WHITE_WHITE
    if config.black_white_char == "":
        config.black_white_char = BLACK_WHITE

    if config.half_blocks:
        _write_half_blocks(config.writer, matrix, size, config)
    elif config.with_sixel:
        _write_sixel(config.writer, matrix, size, config)
    else:
        _write_full_blocks(config.writer, matrix, size, config)


def generate(text, level="H", writer=None):
    config = Config(level=level, writer=writer or sys.stdout,
                    black_char=BLACK, white_char=WHITE,
                    quiet_zone=QUIET_ZONE)
    generate_with_config(text, config)


def generate_half_block(text, level="H", writer=None):
    config = Config(level=level, writer=writer or sys.stdout,
                    half_blocks=True, black_char=BLACK_BLACK,
                    white_black_char=WHITE_BLACK,
                    white_char=WHITE_WHITE,
                    black_white_char=BLACK_WHITE,
                    quiet_zone=QUIET_ZONE)
    generate_with_config(text, config)


def main():
    parser = argparse.ArgumentParser(description="QR code generator for the terminal")
    parser.add_argument("text", nargs="*", help="Text to encode (reads from stdin if empty)")
    parser.add_argument("-v", action="store_true", help="Output debugging information")
    parser.add_argument("-l", default="L", choices=["L", "M", "H"], help="Error correction level")
    parser.add_argument("-q", type=int, default=2, help="Size of quiet zone border")
    parser.add_argument("-s", action="store_true", help="Disable sixel format for output")
    args = parser.parse_args()

    level = args.l.upper()
    content = " ".join(args.text)

    if not content:
        content = sys.stdin.read()

    if args.v:
        print("Level:", level, file=sys.stderr)
        print("Quietzone Border Size:", args.q, file=sys.stderr)
        print("Encoded data:", content, file=sys.stderr)
        print(file=sys.stderr)

    cfg = Config(
        level=level,
        writer=sys.stdout,
        quiet_zone=args.q,
        black_char=BLACK,
        white_char=WHITE,
        with_sixel=False,
    )

    if sys.platform == "win32":
        cfg.black_char = BLACK
        cfg.white_char = WHITE

    print()
    generate_with_config(content, cfg)


if __name__ == "__main__":
    main()
