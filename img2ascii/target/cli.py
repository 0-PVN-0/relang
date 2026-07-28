import argparse
import sys

DEFAULT_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

USAGE_TEXT = (
    "\n"
    "\x1b[1mUsage: img2ascii [options] -i <FILE> [-o <FILE>]\x1b[0m \n\n"
    "A command-line tool for converting images to ASCII art \n\n"
    "Options: \n"
    "   -i, --input  <FILE>     Path of the input image file (required) \n"
    "   -o, --output <FILE>     Path of the output file \n"
    "   -w, --width  <NUMBER>   Width of the output \n"
     "   -c, --chars  <STRING>   Characters to be used for the ASCII image \n"
     "   -g, --grayscale         Display the output in grayscale \n"
     "   -p, --print             Print the output to the console \n"
     "   -r, --reverse           Reverse the string of characters \n"
     "   -d, --debug             Print some useful information \n\n"
)


class _HelpAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        sys.stdout.write(USAGE_TEXT)
        sys.exit(1)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(add_help=False, prog="img2ascii")
    parser.add_argument("-h", "--help", action=_HelpAction, nargs=0)
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output")
    parser.add_argument("-w", "--width", type=int)
    parser.add_argument("-c", "--chars")
    parser.add_argument("-g", "--grayscale", action="store_true")
    parser.add_argument("-p", "--print", action="store_true")
    parser.add_argument("-r", "--reverse", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")

    args = parser.parse_args(argv)

    if args.input is None:
        sys.stdout.write("No input file\n")
        sys.stdout.write(USAGE_TEXT)
        sys.exit(1)

    characters = DEFAULT_CHARS
    if args.chars is not None and len(args.chars) > 0:
        characters = args.chars

    resize_image = False
    desired_width = 0
    if args.width is not None:
        desired_width = args.width
        resize_image = True

    print_flag = args.print or (args.output is None)

    return {
        "input": args.input,
        "output": args.output,
        "width": desired_width,
        "characters": characters,
        "print_flag": print_flag,
        "reverse": args.reverse,
        "grayscale": args.grayscale,
        "debug": args.debug,
        "resize_image": resize_image,
    }
