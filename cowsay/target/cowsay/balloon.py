import re

from .string_width import string_width

SAY_DELIMITERS = {
    "first": ["/", "\\"],
    "middle": ["|", "|"],
    "last": ["\\", "/"],
    "only": ["<", ">"],
}

THINK_DELIMITERS = {
    "first": ["(", ")"],
    "middle": ["(", ")"],
    "last": ["(", ")"],
    "only": ["(", ")"],
}


def say(text, wrap):
    return _format(text, wrap, SAY_DELIMITERS)


def think(text, wrap):
    return _format(text, wrap, THINK_DELIMITERS)


def _format(text, wrap, delimiters):
    lines = _split(text, wrap)
    max_length = _max(lines)

    if len(lines) == 1:
        balloon = [
            " " + _top(max_length),
            delimiters["only"][0] + " " + lines[0] + " " + delimiters["only"][1],
            " " + _bottom(max_length),
        ]
    else:
        balloon = [" " + _top(max_length)]

        for i, line in enumerate(lines):
            if i == 0:
                delim = delimiters["first"]
            elif i == len(lines) - 1:
                delim = delimiters["last"]
            else:
                delim = delimiters["middle"]
            balloon.append(delim[0] + " " + _pad(line, max_length) + " " + delim[1])

        balloon.append(" " + _bottom(max_length))

    return "\n".join(balloon)


def _split(text, wrap):
    text = re.sub(r"\r\n?|[\n\u2028\u2029]", "\n", text)
    text = re.sub(r"^\ufeff", "", text)
    text = text.replace("\t", "        ")

    if not wrap:
        return text.split("\n")

    lines = []
    start = 0
    while start < len(text):
        next_newline = text.find("\n", start)
        if next_newline == -1:
            wrap_at = min(start + wrap, len(text))
        else:
            wrap_at = min(start + wrap, next_newline)

        lines.append(text[start:wrap_at])
        start = wrap_at

        if start < len(text) and text[start] == "\n":
            start += 1

    return lines


def _max(lines):
    max_len = 0
    for line in lines:
        w = string_width(line)
        if w > max_len:
            max_len = w
    return max_len


def _pad(text, length):
    return text + " " * (length - string_width(text))


def _top(length):
    return "_" * (length + 2)


def _bottom(length):
    return "-" * (length + 2)
