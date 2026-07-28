import sys

from PIL import Image


def load_image(filepath, desired_width, resize_image):
    try:
        img = Image.open(filepath).convert("RGB")
    except Exception:
        sys.stderr.write("Could not load image \n")
        sys.exit(1)

    width, height = img.size

    if resize_image:
        if desired_width <= 0:
            sys.stderr.write("Argument 'width' must be greater than 0 \n")
            sys.exit(1)
        if desired_width > width:
            sys.stderr.write(
                "Argument 'width' can not be greater than the original"
                f" image width ({width}px) \n"
            )
            sys.exit(1)

        new_height = int(height / (width / desired_width) / 2)
    else:
        desired_width = width
        new_height = height // 2

    img = img.resize((desired_width, new_height), Image.LANCZOS)
    pixels = list(img.getdata())

    return pixels, desired_width, new_height


def get_intensity(r, g, b):
    return int(round(0.299 * r + 0.587 * g + 0.114 * b))


def get_output_grayscale(pixels, width, height, characters, reverse):
    if reverse:
        characters = characters[::-1]

    char_count = len(characters)
    parts = []

    idx = 0
    for _ in range(height):
        for _ in range(width):
            r, g, b = pixels[idx]
            idx += 1

            intensity = get_intensity(r, g, b)
            char_index = int(intensity / (255 / (char_count - 1)))
            parts.append(characters[char_index])

        parts.append("\n")

    return "".join(parts)


def get_output_rgb(pixels, width, height, characters, reverse):
    if reverse:
        characters = characters[::-1]

    char_count = len(characters)
    parts = []
    r_prev = g_prev = b_prev = -1

    idx = 0
    for _ in range(height):
        for _ in range(width):
            r, g, b = pixels[idx]
            idx += 1

            if not (r == r_prev and g == g_prev and b == b_prev):
                parts.append(f"\x1b[38;2;{r};{g};{b}m")

            r_prev, g_prev, b_prev = r, g, b

            intensity = get_intensity(r, g, b)
            char_index = int(intensity / (255 / (char_count - 1)))
            parts.append(characters[char_index])

        parts.append("\n")

    parts.append("\x1b[0m")
    return "".join(parts)


def write_output(pixels, input_filepath, output_filepath, characters,
                 width, height, flags):

    reverse = flags.get("reverse", False)
    grayscale = flags.get("grayscale", False)
    debug = flags.get("debug", False)
    print_flag = flags.get("print_flag", False)

    if grayscale:
        output = get_output_grayscale(pixels, width, height, characters, reverse)
    else:
        output = get_output_rgb(pixels, width, height, characters, reverse)

    if debug:
        sys.stdout.write(
            f"Input: {input_filepath} \n"
            f"Output: {output_filepath if output_filepath else 'stdout'} \n"
            f"Resolution: {width}x{height} \n"
            f"Characters ({len(characters)}): \"{characters}\" \n"
        )

    if print_flag:
        sys.stdout.write(output)

    if output_filepath is not None:
        try:
            with open(output_filepath, "w") as f:
                f.write(output)
        except OSError as e:
            sys.stderr.write(f"Could not create an output file: {e} \n")
            sys.exit(1)
