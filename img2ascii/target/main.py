import sys

from cli import parse_args, USAGE_TEXT
from converter import load_image, write_output


def main():
    if len(sys.argv) == 1:
        sys.stdout.write("No input file\n")
        sys.stdout.write(USAGE_TEXT)
        sys.exit(1)

    args = parse_args()

    pixels, width, height = load_image(
        args["input"], args["width"], args["resize_image"]
    )

    write_output(
        pixels,
        args["input"],
        args["output"],
        args["characters"],
        width,
        height,
        {
            "reverse": args["reverse"],
            "grayscale": args["grayscale"],
            "debug": args["debug"],
            "print_flag": args["print_flag"],
        },
    )


if __name__ == "__main__":
    main()
