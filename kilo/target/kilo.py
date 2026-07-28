#!/usr/bin/env python3
"""
Kilo -- A very simple text editor in less than 1-kilo lines of code.

Python port of the original C editor by Salvatore Sanfilippo (antirez).
Uses Windows Console API via ctypes for terminal control.
"""

import sys
import os
import ctypes
import ctypes.wintypes
import msvcrt
import atexit
import time
import re
from dataclasses import dataclass, field

KILO_VERSION = "0.0.1"

# Syntax highlight types
HL_NORMAL = 0
HL_NONPRINT = 1
HL_COMMENT = 2
HL_MLCOMMENT = 3
HL_KEYWORD1 = 4
HL_KEYWORD2 = 5
HL_STRING = 6
HL_NUMBER = 7
HL_MATCH = 8

HL_HIGHLIGHT_STRINGS = 1 << 0
HL_HIGHLIGHT_NUMBERS = 1 << 1

# Key action constants
KEY_NULL = 0
CTRL_C = 3
CTRL_D = 4
CTRL_F = 6
CTRL_H = 8
TAB = 9
CTRL_L = 12
ENTER = 13
CTRL_Q = 17
CTRL_S = 19
CTRL_U = 21
ESC = 27
BACKSPACE = 127

ARROW_LEFT = 1000
ARROW_RIGHT = 1001
ARROW_UP = 1002
ARROW_DOWN = 1003
DEL_KEY = 1004
HOME_KEY = 1005
END_KEY = 1006
PAGE_UP = 1007
PAGE_DOWN = 1008

# Windows console constants
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11

ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_LINE_INPUT = 0x0002
ENABLE_ECHO_INPUT = 0x0004
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
ENABLE_WINDOW_INPUT = 0x0008

DISABLE_NEWLINE_AUTO_RETURN = 0x0008

KILO_QUERY_LEN = 256
KILO_QUIT_TIMES = 3

# Windows scan codes for extended keys (prefixed with \xe0 or \x00)
SCAN_UP = 0x48
SCAN_DOWN = 0x50
SCAN_LEFT = 0x4B
SCAN_RIGHT = 0x4D
SCAN_HOME = 0x47
SCAN_END = 0x4F
SCAN_PAGEUP = 0x49
SCAN_PAGEDOWN = 0x51
SCAN_DELETE = 0x53
SCAN_INSERT = 0x52

# Console API types
_GetStdHandle = ctypes.windll.kernel32.GetStdHandle
_GetConsoleMode = ctypes.windll.kernel32.GetConsoleMode
_SetConsoleMode = ctypes.windll.kernel32.SetConsoleMode


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ('dwSize', ctypes.wintypes._COORD),
        ('dwCursorPosition', ctypes.wintypes._COORD),
        ('wAttributes', ctypes.wintypes.WORD),
        ('srWindow', ctypes.wintypes._SMALL_RECT),
        ('dwMaximumWindowSize', ctypes.wintypes._COORD),
    ]


@dataclass
class EditorSyntax:
    filematch: list
    keywords: list
    singleline_comment_start: str
    multiline_comment_start: str
    multiline_comment_end: str
    flags: int


@dataclass
class EditorRow:
    idx: int = 0
    chars: list = field(default_factory=list)
    render: str = ''
    hl: list = field(default_factory=list)
    rsize: int = 0
    hl_oc: int = 0

    @property
    def size(self):
        return len(self.chars)

    @size.setter
    def size(self, value):
        pass


class EditorConfig:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.rowoff = 0
        self.coloff = 0
        self.screenrows = 0
        self.screencols = 0
        self.numrows = 0
        self.rawmode = False
        self.row = []
        self.dirty = 0
        self.filename = ''
        self.statusmsg = ''
        self.statusmsg_time = 0.0
        self.syntax = None


E = EditorConfig()

# --- Syntax Highlighting Database ---
C_HL_extensions = [".c", ".h", ".cpp", ".hpp", ".cc"]

C_HL_keywords = [
    "auto", "break", "case", "continue", "default", "do", "else", "enum",
    "extern", "for", "goto", "if", "register", "return", "sizeof", "static",
    "struct", "switch", "typedef", "union", "volatile", "while", "NULL",
    "alignas", "alignof", "and", "and_eq", "asm", "bitand", "bitor", "class",
    "compl", "constexpr", "const_cast", "deltype", "delete", "dynamic_cast",
    "explicit", "export", "false", "friend", "inline", "mutable", "namespace",
    "new", "noexcept", "not", "not_eq", "nullptr", "operator", "or", "or_eq",
    "private", "protected", "public", "reinterpret_cast", "static_assert",
    "static_cast", "template", "this", "thread_local", "throw", "true", "try",
    "typeid", "typename", "virtual", "xor", "xor_eq",
    "int|", "long|", "double|", "float|", "char|", "unsigned|", "signed|",
    "void|", "short|", "auto|", "const|", "bool|",
]

HLDB = [
    EditorSyntax(
        filematch=C_HL_extensions,
        keywords=C_HL_keywords,
        singleline_comment_start="//",
        multiline_comment_start="/*",
        multiline_comment_end="*/",
        flags=HL_HIGHLIGHT_STRINGS | HL_HIGHLIGHT_NUMBERS,
    )
]


# ======================= Low level terminal handling ==========================

def _get_console_handle(which):
    return _GetStdHandle(which)


def _get_console_mode(handle):
    mode = ctypes.wintypes.DWORD()
    if _GetConsoleMode(handle, ctypes.byref(mode)):
        return mode.value
    return 0


def _set_console_mode(handle, mode):
    return _SetConsoleMode(handle, mode)


def disable_raw_mode():
    if E.rawmode:
        _set_console_mode(_stdin_handle, _orig_stdin_mode)
        _set_console_mode(_stdout_handle, _orig_stdout_mode)
        E.rawmode = False


def editor_at_exit():
    disable_raw_mode()


def enable_raw_mode():
    global _stdin_handle, _stdout_handle, _orig_stdin_mode, _orig_stdout_mode
    if E.rawmode:
        return 0

    _stdin_handle = _get_console_handle(STD_INPUT_HANDLE)
    _stdout_handle = _get_console_handle(STD_OUTPUT_HANDLE)

    if _stdin_handle == ctypes.wintypes.HANDLE(-1).value or _stdout_handle == ctypes.wintypes.HANDLE(-1).value:
        return -1

    _orig_stdin_mode = _get_console_mode(_stdin_handle)
    _orig_stdout_mode = _get_console_mode(_stdout_handle)

    atexit.register(editor_at_exit)

    # Set stdin to raw mode: disable echo, line input, processed input
    new_in_mode = _orig_stdin_mode & ~(ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT | ENABLE_PROCESSED_INPUT)
    if not _set_console_mode(_stdin_handle, new_in_mode):
        return -1

    # Enable VT processing on stdout
    new_out_mode = _orig_stdout_mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING | DISABLE_NEWLINE_AUTO_RETURN
    if not _set_console_mode(_stdout_handle, new_out_mode):
        return -1

    E.rawmode = True
    return 0


_stdin_handle = None
_stdout_handle = None
_orig_stdin_mode = 0
_orig_stdout_mode = 0


def editor_read_key():
    while True:
        prefix = msvcrt.getch()

        # Check for extended key prefix (Windows scan codes)
        if prefix == b'\xe0' or prefix == b'\x00':
            scan = msvcrt.getch()
            if isinstance(scan, bytes):
                code = scan[0]
            else:
                code = ord(scan)
            if code == SCAN_UP:
                return ARROW_UP
            elif code == SCAN_DOWN:
                return ARROW_DOWN
            elif code == SCAN_LEFT:
                return ARROW_LEFT
            elif code == SCAN_RIGHT:
                return ARROW_RIGHT
            elif code == SCAN_HOME:
                return HOME_KEY
            elif code == SCAN_END:
                return END_KEY
            elif code == SCAN_PAGEUP:
                return PAGE_UP
            elif code == SCAN_PAGEDOWN:
                return PAGE_DOWN
            elif code == SCAN_DELETE:
                return DEL_KEY
            else:
                return ESC

        c = prefix[0] if isinstance(prefix, bytes) else ord(prefix)

        if c == ESC:
            # Check if this is the start of an escape sequence using kbhit with timeout
            timeout = 0.1
            start = time.time()
            while time.time() - start < timeout:
                if msvcrt.kbhit():
                    seq1 = msvcrt.getch()
                    seq1 = seq1[0] if isinstance(seq1, bytes) else ord(seq1)
                    seq2 = 0
                    if msvcrt.kbhit():
                        seq2 = msvcrt.getch()
                        seq2 = seq2[0] if isinstance(seq2, bytes) else ord(seq2)
                    else:
                        return ESC

                    if seq1 == ord('['):
                        if seq2 >= ord('0') and seq2 <= ord('9'):
                            if msvcrt.kbhit():
                                seq3 = msvcrt.getch()
                                seq3 = seq3[0] if isinstance(seq3, bytes) else ord(seq3)
                                if seq3 == ord('~'):
                                    if seq2 == ord('3'):
                                        return DEL_KEY
                                    elif seq2 == ord('5'):
                                        return PAGE_UP
                                    elif seq2 == ord('6'):
                                        return PAGE_DOWN
                            return ESC
                        else:
                            if seq2 == ord('A'):
                                return ARROW_UP
                            elif seq2 == ord('B'):
                                return ARROW_DOWN
                            elif seq2 == ord('C'):
                                return ARROW_RIGHT
                            elif seq2 == ord('D'):
                                return ARROW_LEFT
                            elif seq2 == ord('H'):
                                return HOME_KEY
                            elif seq2 == ord('F'):
                                return END_KEY
                    elif seq1 == ord('O'):
                        if seq2 == ord('H'):
                            return HOME_KEY
                        elif seq2 == ord('F'):
                            return END_KEY
                    return ESC
                time.sleep(0.005)
            return ESC
        else:
            return c


def get_cursor_position(rows, cols):
    buf = b''
    sys.stdout.buffer.write(b'\x1b[6n')
    sys.stdout.buffer.flush()

    start = time.time()
    while len(buf) < 32 and (time.time() - start) < 1.0:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            buf += ch
            if ch[-1] == ord('R'):
                break
        time.sleep(0.005)

    if len(buf) < 3 or buf[0] != ESC or buf[1] != ord('['):
        return -1

    try:
        response = buf[2:].decode('ascii').rstrip('R')
        parts = response.split(';')
        if len(parts) == 2:
            rows[0] = int(parts[0])
            cols[0] = int(parts[1])
            return 0
    except (ValueError, UnicodeDecodeError):
        pass
    return -1


def get_window_size():
    try:
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        handle = _get_console_handle(STD_OUTPUT_HANDLE)
        if ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, ctypes.byref(csbi)):
            rows = csbi.srWindow.Bottom - csbi.srWindow.Top + 1
            cols = csbi.srWindow.Right - csbi.srWindow.Left + 1
            if cols > 0 and rows > 0:
                return rows, cols
    except Exception:
        pass

    # Fallback: try cursor position query method
    orig_row = [0]
    orig_col = [0]
    ret = get_cursor_position(orig_row, orig_col)
    if ret == -1:
        return None

    sys.stdout.buffer.write(b'\x1b[999C\x1b[999B')
    sys.stdout.buffer.flush()

    rows = [0]
    cols = [0]
    ret = get_cursor_position(rows, cols)
    if ret == -1:
        return None

    sys.stdout.buffer.write(f'\x1b[{orig_row[0]};{orig_col[0]}H'.encode())
    sys.stdout.buffer.flush()

    return rows[0], cols[0]


def update_window_size():
    size = get_window_size()
    if size is None:
        print("Unable to query the screen for size (columns / rows)", file=sys.stderr)
        sys.exit(1)
    E.screenrows, E.screencols = size
    E.screenrows -= 2


# ====================== Syntax highlight color scheme =========================

def is_separator(c):
    return c == '\0' or c.isspace() or c in ",.()+-/*=~%[];"


def editor_row_has_open_comment(row):
    if row.hl and row.rsize > 0 and row.hl[row.rsize - 1] == HL_MLCOMMENT:
        if row.rsize < 2 or (row.render[row.rsize - 2] != '*' or row.render[row.rsize - 1] != '/'):
            return True
    return False


def editor_update_syntax(row):
    row.hl = [HL_NORMAL] * row.rsize

    if E.syntax is None:
        return

    keywords = E.syntax.keywords
    scs = E.syntax.singleline_comment_start
    mcs = E.syntax.multiline_comment_start
    mce = E.syntax.multiline_comment_end

    render = row.render
    i = 0
    while i < row.rsize and render[i].isspace():
        i += 1

    prev_sep = True
    in_string = 0
    in_comment = False

    if row.idx > 0 and editor_row_has_open_comment(E.row[row.idx - 1]):
        in_comment = True

    while i < row.rsize:
        ch = render[i]

        # Handle // comments
        if prev_sep and scs and render[i:i + 2] == scs:
            for j in range(i, row.rsize):
                row.hl[j] = HL_COMMENT
            return

        # Handle multi-line comments
        if in_comment:
            row.hl[i] = HL_MLCOMMENT
            if mce and row.rsize - i >= 2 and render[i:i + 2] == mce:
                row.hl[i + 1] = HL_MLCOMMENT
                i += 2
                in_comment = False
                prev_sep = True
                continue
            else:
                prev_sep = False
                i += 1
                continue
        elif mcs and row.rsize - i >= 2 and render[i:i + 2] == mcs:
            row.hl[i] = HL_MLCOMMENT
            row.hl[i + 1] = HL_MLCOMMENT
            i += 2
            in_comment = True
            prev_sep = False
            continue

        # Handle strings
        if in_string:
            row.hl[i] = HL_STRING
            if ch == '\\':
                if i + 1 < row.rsize:
                    row.hl[i + 1] = HL_STRING
                    i += 2
                    prev_sep = False
                    continue
            if ch == in_string:
                in_string = 0
            i += 1
            continue
        else:
            if E.syntax.flags & HL_HIGHLIGHT_STRINGS and (ch == '"' or ch == "'"):
                in_string = ch
                row.hl[i] = HL_STRING
                i += 1
                prev_sep = False
                continue

        # Handle non-printable chars
        if not ch.isprintable() and ch not in ('\t', '\n', '\r'):
            row.hl[i] = HL_NONPRINT
            i += 1
            prev_sep = False
            continue

        # Handle numbers
        if E.syntax.flags & HL_HIGHLIGHT_NUMBERS:
            if ch.isdigit() and (prev_sep or (i > 0 and row.hl[i - 1] == HL_NUMBER)):
                row.hl[i] = HL_NUMBER
                i += 1
                prev_sep = False
                continue
            if ch == '.' and i > 0 and row.hl[i - 1] == HL_NUMBER:
                row.hl[i] = HL_NUMBER
                i += 1
                prev_sep = False
                continue

        # Handle keywords and lib calls
        if prev_sep and keywords:
            matched = False
            for kw in keywords:
                kw2 = kw.endswith('|')
                klen = len(kw) - (1 if kw2 else 0)
                if i + klen <= row.rsize and render[i:i + klen] == kw[:klen]:
                    if i + klen >= row.rsize or is_separator(render[i + klen]):
                        hl_type = HL_KEYWORD2 if kw2 else HL_KEYWORD1
                        for j in range(klen):
                            row.hl[i + j] = hl_type
                        i += klen
                        matched = True
                        break
            if matched:
                prev_sep = False
                continue

        prev_sep = is_separator(ch)
        i += 1

    oc = 1 if editor_row_has_open_comment(row) else 0
    if row.hl_oc != oc and row.idx + 1 < E.numrows:
        editor_update_syntax(E.row[row.idx + 1])
    row.hl_oc = oc


def editor_syntax_to_color(hl):
    mapping = {
        HL_COMMENT: 36,
        HL_MLCOMMENT: 36,
        HL_KEYWORD1: 33,
        HL_KEYWORD2: 32,
        HL_STRING: 35,
        HL_NUMBER: 31,
        HL_MATCH: 34,
    }
    return mapping.get(hl, 37)


def editor_select_syntax_highlight(filename):
    E.syntax = None
    for s in HLDB:
        for pat in s.filematch:
            p = filename.find(pat)
            if p != -1:
                if pat[0] != '.' or p + len(pat) == len(filename):
                    E.syntax = s
                    return


# ======================= Editor rows implementation ===========================

def editor_update_row(row):
    tabs = 0
    for ch in row.chars:
        if ch == '\t':
            tabs += 1

    alloc = len(row.chars) + tabs * 8 + 1
    if alloc > 2**32:
        print("Some line of the edited file is too long for kilo", file=sys.stderr)
        sys.exit(1)

    render_chars = []
    for ch in row.chars:
        if ch == '\t':
            render_chars.append(' ')
            while (len(render_chars)) % 8 != 0:
                render_chars.append(' ')
        else:
            render_chars.append(ch)

    row.render = ''.join(render_chars)
    row.rsize = len(row.render)

    editor_update_syntax(row)


def editor_insert_row(at, s):
    if at > E.numrows:
        return

    new_row = EditorRow()
    new_row.chars = list(s)
    new_row.idx = at

    E.row.insert(at, new_row)
    for j in range(at + 1, E.numrows + 1):
        E.row[j].idx = j

    editor_update_row(E.row[at])
    E.numrows += 1
    E.dirty += 1


def editor_free_row(row):
    row.chars = []
    row.render = ''
    row.hl = []


def editor_del_row(at):
    if at >= E.numrows:
        return
    editor_free_row(E.row[at])
    del E.row[at]
    for j in range(at, E.numrows - 1):
        E.row[j].idx = j
    E.numrows -= 1
    E.dirty += 1


def editor_rows_to_string():
    lines = []
    for row in E.row:
        lines.append(''.join(row.chars))
    return '\n'.join(lines)


def editor_row_insert_char(row, at, c):
    if isinstance(c, int):
        c = chr(c)

    if at > len(row.chars):
        padlen = at - len(row.chars)
        row.chars.extend([' '] * padlen)
        row.chars.append(c)
    else:
        row.chars.insert(at, c)
    editor_update_row(row)
    E.dirty += 1


def editor_row_append_string(row, s):
    row.chars.extend(list(s))
    editor_update_row(row)
    E.dirty += 1


def editor_row_del_char(row, at):
    if len(row.chars) <= at:
        return
    del row.chars[at]
    editor_update_row(row)
    E.dirty += 1


def editor_insert_char(c):
    filerow = E.rowoff + E.cy
    filecol = E.coloff + E.cx

    if filerow >= E.numrows:
        while E.numrows <= filerow:
            editor_insert_row(E.numrows, "")

    row = E.row[filerow]
    editor_row_insert_char(row, filecol, c)

    if E.cx == E.screencols - 1:
        E.coloff += 1
    else:
        E.cx += 1
    E.dirty += 1


def editor_insert_newline():
    filerow = E.rowoff + E.cy
    filecol = E.coloff + E.cx

    if filerow >= E.numrows:
        if filerow == E.numrows:
            editor_insert_row(filerow, "")
            if E.cy == E.screenrows - 1:
                E.rowoff += 1
            else:
                E.cy += 1
            E.cx = 0
            E.coloff = 0
        return

    row = E.row[filerow]
    if filecol >= row.size:
        filecol = row.size

    if filecol == 0:
        editor_insert_row(filerow, "")
    else:
        remaining = ''.join(row.chars[filecol:])
        editor_insert_row(filerow + 1, remaining)
        row = E.row[filerow]
        row.chars = row.chars[:filecol]
        editor_update_row(row)

    if E.cy == E.screenrows - 1:
        E.rowoff += 1
    else:
        E.cy += 1
    E.cx = 0
    E.coloff = 0


def editor_del_char():
    filerow = E.rowoff + E.cy
    filecol = E.coloff + E.cx

    if filerow >= E.numrows:
        return

    row = E.row[filerow]

    if not row or (filecol == 0 and filerow == 0):
        return

    if filecol == 0:
        filecol = E.row[filerow - 1].size
        editor_row_append_string(E.row[filerow - 1], ''.join(row.chars))
        editor_del_row(filerow)
        if E.cy == 0:
            E.rowoff -= 1
        else:
            E.cy -= 1
        E.cx = filecol
        if E.cx >= E.screencols:
            shift = (E.screencols - E.cx) + 1
            E.cx -= shift
            E.coloff += shift
    else:
        editor_row_del_char(row, filecol - 1)
        if E.cx == 0 and E.coloff:
            E.coloff -= 1
        else:
            E.cx -= 1

    if row:
        editor_update_row(row)
    E.dirty += 1


# ============================= File I/O =======================================

def editor_open(filename):
    E.dirty = 0
    E.filename = filename

    if not os.path.exists(filename):
        return 1

    with open(filename, 'r', encoding='utf-8', errors='replace') as fp:
        for line in fp:
            linelen = len(line)
            if linelen > 0 and (line[-1] == '\n' or line[-1] == '\r'):
                line = line[:-1]
            editor_insert_row(E.numrows, line)

    E.dirty = 0
    return 0


def editor_save():
    text = editor_rows_to_string()
    data = (text + '\n').encode('utf-8')

    try:
        with open(E.filename, 'wb') as fp:
            fp.write(data)
    except IOError as e:
        editor_set_status_message("Can't save! I/O error: %s" % str(e))
        return 1

    E.dirty = 0
    editor_set_status_message("%d bytes written on disk" % len(data))
    return 0


# ============================= Terminal update ================================

def editor_refresh_screen():
    ab = []

    ab.append('\x1b[?25l')  # Hide cursor
    ab.append('\x1b[H')  # Go home

    for y in range(E.screenrows):
        filerow = E.rowoff + y

        if filerow >= E.numrows:
            if E.numrows == 0 and y == E.screenrows // 3:
                welcome = "Kilo editor -- version %s\x1b[0K\r\n" % KILO_VERSION
                padding = (E.screencols - len(welcome)) // 2
                if padding:
                    ab.append('~')
                    padding -= 1
                ab.append(' ' * padding)
                ab.append(welcome)
            else:
                ab.append('~\x1b[0K\r\n')
            continue

        r = E.row[filerow]

        coloff = E.coloff
        if coloff >= r.rsize:
            len_val = 0
        else:
            len_val = r.rsize - coloff

        current_color = -1
        if len_val > 0:
            if len_val > E.screencols:
                len_val = E.screencols
            c = r.render[coloff:coloff + len_val]

            for j in range(len_val):
                hl_idx = coloff + j
                hl_type = r.hl[hl_idx] if hl_idx < len(r.hl) else HL_NORMAL

                if hl_type == HL_NONPRINT:
                    sym = '@' + chr(ord(c[j]) - 0x40) if ' ' <= c[j] <= '~' and ord(c[j]) <= 26 else '?'
                    ab.append('\x1b[7m')
                    ab.append(sym)
                    ab.append('\x1b[0m')
                elif hl_type == HL_NORMAL:
                    if current_color != -1:
                        ab.append('\x1b[39m')
                        current_color = -1
                    ab.append(c[j])
                else:
                    color = editor_syntax_to_color(hl_type)
                    if color != current_color:
                        ab.append('\x1b[%dm' % color)
                        current_color = color
                    ab.append(c[j])

        ab.append('\x1b[39m')
        ab.append('\x1b[0K')
        ab.append('\r\n')

    # Status bar: first row
    ab.append('\x1b[0K')
    ab.append('\x1b[7m')
    filename_display = E.filename if E.filename else "[No Name]"
    status = "%.20s - %d lines %s" % (filename_display, E.numrows, "(modified)" if E.dirty else "")
    rstatus = "%d/%d" % (E.rowoff + E.cy + 1, E.numrows)

    if len(status) > E.screencols:
        status = status[:E.screencols]
    ab.append(status)

    while len(status) < E.screencols:
        if E.screencols - len(status) == len(rstatus):
            ab.append(rstatus)
            break
        else:
            ab.append(' ')
            len(status)
            status += ' '
    ab.append('\x1b[0m\r\n')

    # Status bar: second row (message)
    ab.append('\x1b[0K')
    if E.statusmsg and time.time() - E.statusmsg_time < 5:
        msglen = len(E.statusmsg)
        ab.append(E.statusmsg[:E.screencols] if msglen > E.screencols else E.statusmsg)

    # Position cursor
    cx = 1
    filerow = E.rowoff + E.cy
    if filerow < E.numrows:
        row = E.row[filerow]
        for j in range(E.coloff, E.cx + E.coloff):
            if j < row.size and row.chars[j] == '\t':
                cx += 7 - (cx % 8)
            cx += 1

    ab.append('\x1b[%d;%dH' % (E.cy + 1, cx))
    ab.append('\x1b[?25h')  # Show cursor

    sys.stdout.buffer.write(''.join(ab).encode('utf-8'))
    sys.stdout.buffer.flush()


def editor_set_status_message(fmt, *args):
    E.statusmsg = fmt % args if args else fmt
    E.statusmsg_time = time.time()


# =============================== Find mode ====================================

def editor_find():
    query = ''
    last_match = -1
    find_next = 0
    saved_hl_line = -1
    saved_hl = None

    saved_cx = E.cx
    saved_cy = E.cy
    saved_coloff = E.coloff
    saved_rowoff = E.rowoff

    while True:
        editor_set_status_message("Search: %s (Use ESC/Arrows/Enter)" % query)
        editor_refresh_screen()

        c = editor_read_key()
        if c in (DEL_KEY, CTRL_H, BACKSPACE):
            if len(query) > 0:
                query = query[:-1]
                last_match = -1
        elif c in (ESC, ENTER):
            if c == ESC:
                E.cx = saved_cx
                E.cy = saved_cy
                E.coloff = saved_coloff
                E.rowoff = saved_rowoff
            # Restore saved HL
            if saved_hl is not None:
                E.row[saved_hl_line].hl = saved_hl
                saved_hl = None
            editor_set_status_message("")
            return
        elif c in (ARROW_RIGHT, ARROW_DOWN):
            find_next = 1
        elif c in (ARROW_LEFT, ARROW_UP):
            find_next = -1
        elif 32 <= c <= 126:
            if len(query) < KILO_QUERY_LEN:
                query += chr(c)
                last_match = -1

        if last_match == -1:
            find_next = 1
        if find_next:
            match = None
            match_offset = 0
            current = last_match

            for _ in range(E.numrows):
                current += find_next
                if current == -1:
                    current = E.numrows - 1
                elif current == E.numrows:
                    current = 0
                pos = E.row[current].render.find(query)
                if pos != -1:
                    match = current
                    match_offset = pos
                    break

            find_next = 0

            # Restore saved HL, then set new
            if saved_hl is not None:
                E.row[saved_hl_line].hl = saved_hl
                saved_hl = None

            if match is not None:
                row = E.row[match]
                last_match = match
                if row.hl:
                    saved_hl_line = match
                    saved_hl = row.hl[:]
                    for j in range(match_offset, match_offset + len(query)):
                        if j < len(row.hl):
                            row.hl[j] = HL_MATCH

                E.cy = 0
                E.cx = match_offset
                E.rowoff = match
                E.coloff = 0
                if E.cx > E.screencols:
                    diff = E.cx - E.screencols
                    E.cx -= diff
                    E.coloff += diff


# ========================= Editor events handling =============================

def editor_move_cursor(key):
    filerow = E.rowoff + E.cy
    filecol = E.coloff + E.cx

    if key == ARROW_LEFT:
        if E.cx == 0:
            if E.coloff:
                E.coloff -= 1
            else:
                if filerow > 0:
                    E.cy -= 1
                    E.cx = E.row[filerow - 1].size
                    if E.cx > E.screencols - 1:
                        E.coloff = E.cx - E.screencols + 1
                        E.cx = E.screencols - 1
        else:
            E.cx -= 1

    elif key == ARROW_RIGHT:
        if filerow < E.numrows:
            row = E.row[filerow]
            if filecol < row.size:
                if E.cx == E.screencols - 1:
                    E.coloff += 1
                else:
                    E.cx += 1
            elif filecol == row.size:
                E.cx = 0
                E.coloff = 0
                if E.cy == E.screenrows - 1:
                    E.rowoff += 1
                else:
                    E.cy += 1

    elif key == ARROW_UP:
        if E.cy == 0:
            if E.rowoff:
                E.rowoff -= 1
        else:
            E.cy -= 1

    elif key == ARROW_DOWN:
        if filerow < E.numrows:
            if E.cy == E.screenrows - 1:
                E.rowoff += 1
            else:
                E.cy += 1

    # Fix cx if current line has not enough chars
    filerow = E.rowoff + E.cy
    filecol = E.coloff + E.cx
    if filerow < E.numrows:
        rowlen = E.row[filerow].size
    else:
        rowlen = 0
    if filecol > rowlen:
        E.cx -= filecol - rowlen
        if E.cx < 0:
            E.coloff += E.cx
            E.cx = 0


def editor_process_keypress():
    global quit_times
    c = editor_read_key()

    if c == ENTER:
        editor_insert_newline()
    elif c == CTRL_C:
        pass
    elif c == CTRL_Q:
        if E.dirty and quit_times > 0:
            editor_set_status_message(
                "WARNING!!! File has unsaved changes. "
                "Press Ctrl-Q %d more times to quit." % quit_times)
            quit_times -= 1
            return
        disable_raw_mode()
        sys.exit(0)
    elif c == CTRL_S:
        editor_save()
    elif c == CTRL_F:
        editor_find()
    elif c in (BACKSPACE, CTRL_H, DEL_KEY):
        editor_del_char()
    elif c in (PAGE_UP, PAGE_DOWN):
        if c == PAGE_UP and E.cy != 0:
            E.cy = 0
        elif c == PAGE_DOWN and E.cy != E.screenrows - 1:
            E.cy = E.screenrows - 1
        times = E.screenrows
        direction = ARROW_UP if c == PAGE_UP else ARROW_DOWN
        for _ in range(times):
            editor_move_cursor(direction)
    elif c in (ARROW_UP, ARROW_DOWN, ARROW_LEFT, ARROW_RIGHT):
        editor_move_cursor(c)
    elif c == CTRL_L:
        pass
    elif c == ESC:
        pass
    else:
        editor_insert_char(c)

    quit_times = KILO_QUIT_TIMES


quit_times = KILO_QUIT_TIMES


# =============================== Init =========================================

def init_editor():
    E.cx = 0
    E.cy = 0
    E.rowoff = 0
    E.coloff = 0
    E.numrows = 0
    E.row = []
    E.dirty = 0
    E.filename = ''
    E.syntax = None
    update_window_size()


def handle_sigwinch(signum, frame):
    update_window_size()
    if E.cy > E.screenrows:
        E.cy = E.screenrows - 1
    if E.cx > E.screencols:
        E.cx = E.screencols - 1
    editor_refresh_screen()


# =============================== Main =========================================

def main():
    if len(sys.argv) != 2:
        print("Usage: kilo <filename>", file=sys.stderr)
        sys.exit(1)

    init_editor()
    editor_select_syntax_highlight(sys.argv[1])
    editor_open(sys.argv[1])
    if enable_raw_mode() == -1:
        print("Unable to enter raw mode", file=sys.stderr)
        sys.exit(1)

    editor_set_status_message(
        "HELP: Ctrl-S = save | Ctrl-Q = quit | Ctrl-F = find")

    try:
        while True:
            editor_refresh_screen()
            editor_process_keypress()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        disable_raw_mode()


if __name__ == '__main__':
    main()