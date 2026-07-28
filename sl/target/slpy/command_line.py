import shutil
import sys
import time
from slpy import sl


def main():
    size = shutil.get_terminal_size(fallback=(80, 24))
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    for frame in sl(size.columns, size.lines, arg):
        print(frame)
        time.sleep(0.04)


if __name__ == '__main__':
    main()
