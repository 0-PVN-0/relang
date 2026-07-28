#!/usr/bin/env python3
import argparse
import sys

from cowsay import say, think, list as list_cows

COWSAY_MODES = {
    "b": "Mode: Borg",
    "d": "Mode: Dead",
    "g": "Mode: Greedy",
    "p": "Mode: Paranoia",
    "s": "Mode: Stoned",
    "t": "Mode: Tired",
    "w": "Mode: Wired",
    "y": "Mode: Youthful",
}


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cowsay",
        usage="""%(prog)s [-e eye_string] [-f cowfile] [-h] [-l] [-n] [-T tongue_string] [-W column] [-bdgpstwy] text

If any command-line arguments are left over after all switches have been processed, they become the cow's message.

If the program is invoked as cowthink then the cow will think its message instead of saying it.""",
        add_help=False,
    )

    parser.add_argument("-e", default="oo", help="Select the appearance of the cow's eyes.")
    parser.add_argument("-T", default="  ", help="The tongue is configurable similarly to the eyes through -T and tongue_string.")
    parser.add_argument("-W", default=40, type=int, help="Specifies roughly where the message should be wrapped. The default is equivalent to -W 40 i.e. wrap words at or before the 40th column.")
    parser.add_argument("-f", default="default", help="Specifies a cow picture file (''cowfile'') to use. It can be either a path to a cow file or the name of one of cows included in the package.")
    parser.add_argument("-n", action="store_true", help="If it is specified, the given message will not be word-wrapped.")
    parser.add_argument("-l", action="store_true", help="List all cowfiles included in this package.")
    parser.add_argument("-r", action="store_true", help="Select a random cow")
    parser.add_argument("--think", action="store_true", help="Think the message instead of saying it aloud.")
    parser.add_argument("-h", "--help", action="store_true", help="Display this help message")

    for mode in COWSAY_MODES:
        parser.add_argument(f"-{mode}", action="store_true", dest=mode, help=COWSAY_MODES[mode])

    parser.add_argument("text", nargs="*", help="Message for the cow to say")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    options = vars(args)

    if args.help:
        parser.print_help()
        return

    if args.l:
        names = list_cows()
        print("  ".join(names))
        return

    text = " ".join(args.text) if args.text else None

    if text:
        options["text"] = text
        _say(options)
    else:
        data = sys.stdin.read()
        if data:
            data = data.removesuffix("\r\n").removesuffix("\n").removesuffix("\r")
            options["text"] = data
            _say(options)
        else:
            parser.print_help()


def _say(options):
    is_think = options.pop("think", False)
    result = think(options) if is_think else say(options)
    print(result, end="" if result.endswith("\n") else None)


if __name__ == "__main__":
    main()
