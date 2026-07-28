"""7-segment Unicode big number display for terminal, matching the Go bignum package."""

HEIGHT = 5
WIDTH = 4

_NUMBERS_RAW = """
 \u2501\u2501
\u2503  \u2503

\u2503  \u2503
 \u2501\u2501


   \u2503

   \u2503


 \u2501\u2501
   \u2503
 \u2501\u2501
\u2503
 \u2501\u2501

 \u2501\u2501
   \u2503
 \u2501\u2501
   \u2503
 \u2501\u2501


\u2503  \u2503
 \u2501\u2501
   \u2503


 \u2501\u2501
\u2503
 \u2501\u2501
   \u2503
 \u2501\u2501

 \u2501\u2501
\u2503
 \u2501\u2501
\u2503  \u2503
 \u2501\u2501

 \u2501\u2501
   \u2503

   \u2503


 \u2501\u2501
\u2503  \u2503
 \u2501\u2501
\u2503  \u2503
 \u2501\u2501

 \u2501\u2501
\u2503  \u2503
 \u2501\u2501
   \u2503
 \u2501\u2501



::



..



"""

_NUMBER_LINES = _NUMBERS_RAW.split("\n")[1:]

for i in range(len(_NUMBER_LINES)):
    extra = -1 if i >= 10 * (HEIGHT + 1) else 1
    target_len = WIDTH + extra
    current_len = len(_NUMBER_LINES[i])
    if current_len < target_len:
        _NUMBER_LINES[i] += " " * (target_len - current_len)


class Display:
    def __init__(self):
        self._lines = [""] * HEIGHT

    def __str__(self):
        return "\n".join(self._lines)

    def place_digit(self, ch, blink=False):
        if ch.isdigit():
            digit = int(ch)
        else:
            digit = 11 if blink else 10
        start = digit * (HEIGHT + 1)
        for i in range(HEIGHT):
            self._lines[i] += _NUMBER_LINES[start + i]


def time_string(num_str, blink):
    d = Display()
    for ch in num_str:
        d.place_digit(ch, blink)
    return str(d)
