import random as _random

D51HEIGHT = 10
D51FUNNEL = 7
D51LENGTH = 83
D51PATTERNS = 6

D51STR1 = "      ====        ________                ___________ "
D51STR2 = "  _D _|  |_______/        \\__I_I_____===__|_________| "
D51STR3 = "   |(_)---  |   H\\________/ |   |        =|___ ___|   "
D51STR4 = "   /     |  |   H  |  |     |   |         ||_| |_||   "
D51STR5 = "  |      |  |   H  |__--------------------| [___] |   "
D51STR6 = "  | ________|___H__/__|_____/[][]~\\_______|       |   "
D51STR7 = "  |/ |   |-----------I_____I [][] []  D   |=======|__ "

D51WHL11 = "__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ "
D51WHL12 = " |/-=|___|=    ||    ||    ||    |_____/~\\___/        "
D51WHL13 = "  \\_/      \\O=====O=====O=====O_/      \\_/            "

D51WHL21 = "__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ "
D51WHL22 = " |/-=|___|=O=====O=====O=====O   |_____/~\\___/        "
D51WHL23 = "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "

D51WHL31 = "__/ =| o |=-O=====O=====O=====O \\ ____Y___________|__ "
D51WHL32 = " |/-=|___|=    ||    ||    ||    |_____/~\\___/        "
D51WHL33 = "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "

D51WHL41 = "__/ =| o |=-~O=====O=====O=====O\\ ____Y___________|__ "
D51WHL42 = " |/-=|___|=    ||    ||    ||    |_____/~\\___/        "
D51WHL43 = "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "

D51WHL51 = "__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ "
D51WHL52 = " |/-=|___|=   O=====O=====O=====O|_____/~\\___/        "
D51WHL53 = "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "

D51WHL61 = "__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ "
D51WHL62 = " |/-=|___|=    ||    ||    ||    |_____/~\\___/        "
D51WHL63 = "  \\_/      \\_O=====O=====O=====O/      \\_/            "

D51DEL = "                                                      "

COAL01 = "                              "
COAL02 = "                              "
COAL03 = "    _________________         "
COAL04 = "   _|                \\_____A  "
COAL05 = " =|                        |  "
COAL06 = " -|                        |  "
COAL07 = "__|________________________|_ "
COAL08 = "|__________________________|_ "
COAL09 = "   |_D__D__D_|  |_D__D__D_|   "
COAL10 = "    \\_/   \\_/    \\_/   \\_/    "

COALDEL = "                              "

LOGOHEIGHT = 6
LOGOFUNNEL = 4
LOGOLENGTH = 84
LOGOPATTERNS = 6

LOGO1 = "     ++      +------ "
LOGO2 = "     ||      |+-+ |  "
LOGO3 = "   /---------|| | |  "
LOGO4 = "  + ========  +-+ |  "

LWHL11 = " _|--O========O~\\-+  "
LWHL12 = "//// \\_/      \\_/    "

LWHL21 = " _|--/O========O\\-+  "
LWHL22 = "//// \\_/      \\_/    "

LWHL31 = " _|--/~O========O-+  "
LWHL32 = "//// \\_/      \\_/    "

LWHL41 = " _|--/~\\------/~\\-+  "
LWHL42 = "//// \\_O========O    "

LWHL51 = " _|--/~\\------/~\\-+  "
LWHL52 = "//// \\O========O/    "

LWHL61 = " _|--/~\\------/~\\-+  "
LWHL62 = "//// O========O_/    "

LCOAL1 = "____                 "
LCOAL2 = "|   \\@@@@@@@@@@@     "
LCOAL3 = "|    \\@@@@@@@@@@@@@_ "
LCOAL4 = "|                  | "
LCOAL5 = "|__________________| "
LCOAL6 = "   (O)       (O)     "

LCAR1 = "____________________ "
LCAR2 = "|  ___ ___ ___ ___ | "
LCAR3 = "|  |_| |_| |_| |_| | "
LCAR4 = "|__________________| "
LCAR5 = "|__________________| "
LCAR6 = "   (O)        (O)    "

DELLN = "                     "

C51HEIGHT = 11
C51FUNNEL = 7
C51LENGTH = 87
C51PATTERNS = 6

C51DEL = "                                                       "

C51STR1 = "        ___                                            "
C51STR2 = "       _|_|_  _     __       __             ___________"
C51STR3 = "    D__/   \\_(_)___|  |__H__|  |_____I_Ii_()|_________|"
C51STR4 = "     | `---'   |:: `--'  H  `--'         |  |___ ___|  "
C51STR5 = "    +|~~~~~~~~++::~~~~~~~H~~+=====+~~~~~~|~~||_| |_||  "
C51STR6 = "    ||        | ::       H  +=====+      |  |::  ...|  "
C51STR7 = "|    | _______|_::-----------------[][]-----|       |  "

C51WH11 = "| /~~ ||   |-----/~~~~\\  /[I_____I][][] --|||_______|__"
C51WH12 = "------'|oOo|=[]=-      ||      ||      |  ||=======_|__"
C51WH13 = "/~\\____|___|/~\\_|  O=======O=======O   |__|+-/~\\_|     "
C51WH14 = "\\_/         \\_/  \\____/  \\____/  \\____/      \\_/       "

C51WH21 = "| /~~ ||   |-----/~~~~\\  /[I_____I][][] --|||_______|__"
C51WH22 = "------'|oOo|=[]=- O=======O=======O    |  ||=======_|__"
C51WH23 = "/~\\____|___|/~\\_|      ||      ||      |__|+-/~\\_|     "
C51WH24 = "\\_/         \\_/  \\____/  \\____/  \\____/      \\_/       "

C51WH31 = "| /~~ ||   |-----/~~~~\\  /[I_____I][][] --|||_______|__"
C51WH32 = "------'|oOo|==[]=- O=======O=======O   |  ||=======_|__"
C51WH33 = "/~\\____|___|/~\\_|      ||      ||      |__|+-/~\\_|     "
C51WH34 = "\\_/         \\_/  \\____/  \\____/  \\____/      \\_/       "

C51WH41 = "| /~~ ||   |-----/~~~~\\  /[I_____I][][] --|||_______|__"
C51WH42 = "------'|oOo|===[]=- O=======O=======O  |  ||=======_|__"
C51WH43 = "/~\\____|___|/~\\_|      ||      ||      |__|+-/~\\_|     "
C51WH44 = "\\_/         \\_/  \\____/  \\____/  \\____/      \\_/       "

C51WH51 = "| /~~ ||   |-----/~~~~\\  /[I_____I][][] --|||_______|__"
C51WH52 = "------'|oOo|===[]=-    ||      ||      |  ||=======_|__"
C51WH53 = "/~\\____|___|/~\\_|    O=======O=======O |__|+-/~\\_|     "
C51WH54 = "\\_/         \\_/  \\____/  \\____/  \\____/      \\_/       "

C51WH61 = "| /~~ ||   |-----/~~~~\\  /[I_____I][][] --|||_______|__"
C51WH62 = "------'|oOo|==[]=-     ||      ||      |  ||=======_|__"
C51WH63 = "/~\\____|___|/~\\_|   O=======O=======O  |__|+-/~\\_|     "
C51WH64 = "\\_/         \\_/  \\____/  \\____/  \\____/      \\_/       "

SMOKEPTNS = 16

SMOKE0 = [
    "(   )", "(    )", "(    )", "(   )", "(  )",
    "(  )", "( )", "( )", "()", "()",
    "O", "O", "O", "O", "O",
    " ",
]

SMOKE1 = [
    "(@@@)", "(@@@@)", "(@@@@)", "(@@@)", "(@@)",
    "(@@)", "(@)", "(@)", "@@", "@@",
    "@", "@", "@", "@", "@",
    " ",
]

SMOKE_DY = [2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
SMOKE_DX = [-2, -1, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3]

D51_PATTERNS = [
    [D51STR1, D51STR2, D51STR3, D51STR4, D51STR5, D51STR6, D51STR7,
     D51WHL11, D51WHL12, D51WHL13, D51DEL],
    [D51STR1, D51STR2, D51STR3, D51STR4, D51STR5, D51STR6, D51STR7,
     D51WHL21, D51WHL22, D51WHL23, D51DEL],
    [D51STR1, D51STR2, D51STR3, D51STR4, D51STR5, D51STR6, D51STR7,
     D51WHL31, D51WHL32, D51WHL33, D51DEL],
    [D51STR1, D51STR2, D51STR3, D51STR4, D51STR5, D51STR6, D51STR7,
     D51WHL41, D51WHL42, D51WHL43, D51DEL],
    [D51STR1, D51STR2, D51STR3, D51STR4, D51STR5, D51STR6, D51STR7,
     D51WHL51, D51WHL52, D51WHL53, D51DEL],
    [D51STR1, D51STR2, D51STR3, D51STR4, D51STR5, D51STR6, D51STR7,
     D51WHL61, D51WHL62, D51WHL63, D51DEL],
]

D51_COAL = [COAL01, COAL02, COAL03, COAL04, COAL05,
            COAL06, COAL07, COAL08, COAL09, COAL10, COALDEL]

LOGO_SL_PATTERNS = [
    [LOGO1, LOGO2, LOGO3, LOGO4, LWHL11, LWHL12, DELLN],
    [LOGO1, LOGO2, LOGO3, LOGO4, LWHL21, LWHL22, DELLN],
    [LOGO1, LOGO2, LOGO3, LOGO4, LWHL31, LWHL32, DELLN],
    [LOGO1, LOGO2, LOGO3, LOGO4, LWHL41, LWHL42, DELLN],
    [LOGO1, LOGO2, LOGO3, LOGO4, LWHL51, LWHL52, DELLN],
    [LOGO1, LOGO2, LOGO3, LOGO4, LWHL61, LWHL62, DELLN],
]

LOGO_COAL = [LCOAL1, LCOAL2, LCOAL3, LCOAL4, LCOAL5, LCOAL6, DELLN]
LOGO_CAR = [LCAR1, LCAR2, LCAR3, LCAR4, LCAR5, LCAR6, DELLN]

C51_PATTERNS = [
    [C51STR1, C51STR2, C51STR3, C51STR4, C51STR5, C51STR6, C51STR7,
     C51WH11, C51WH12, C51WH13, C51WH14, C51DEL],
    [C51STR1, C51STR2, C51STR3, C51STR4, C51STR5, C51STR6, C51STR7,
     C51WH21, C51WH22, C51WH23, C51WH24, C51DEL],
    [C51STR1, C51STR2, C51STR3, C51STR4, C51STR5, C51STR6, C51STR7,
     C51WH31, C51WH32, C51WH33, C51WH34, C51DEL],
    [C51STR1, C51STR2, C51STR3, C51STR4, C51STR5, C51STR6, C51STR7,
     C51WH41, C51WH42, C51WH43, C51WH44, C51DEL],
    [C51STR1, C51STR2, C51STR3, C51STR4, C51STR5, C51STR6, C51STR7,
     C51WH51, C51WH52, C51WH53, C51WH54, C51DEL],
    [C51STR1, C51STR2, C51STR3, C51STR4, C51STR5, C51STR6, C51STR7,
     C51WH61, C51WH62, C51WH63, C51WH64, C51DEL],
]

C51_COAL = [COALDEL, COAL01, COAL02, COAL03, COAL04, COAL05,
            COAL06, COAL07, COAL08, COAL09, COAL10, COALDEL]

MAN = [["", "(O)"], ["Help!", "\\O/"]]

MDANCER = [["_O_", " #", "/\\"], ["(0)", " #", "/\\"], ["(O_", " #", "/\\"]]
EMDANCER = [["   ", "  ", "  "], ["   ", "  ", "  "], ["   ", "  ", "  "]]

FDANCER = [["\\\\0", "/\\", "|\\"], ["0//", "/\\", "/|"]]
EFDANCER = [["   ", "  ", "  "], ["   ", "  ", "  "]]


class _Engine:
    def __init__(self, cols, lines, arg=""):
        self.COLS = cols
        self.LINES = lines
        self.ACCIDENT = 0
        self.LOGO = 0
        self.FLY = 0
        self.C51 = 0
        self.DANCE = 0
        self.RAND = 0
        self._parse_args(arg)
        if self.RAND:
            self.ACCIDENT |= _random.randint(0, 1)
            self.LOGO |= _random.randint(0, 1)
            self.FLY |= _random.randint(0, 1)
            self.C51 |= _random.randint(0, 1)
            self.DANCE |= _random.randint(0, 1)
        self.N = self._count_frames()
        self._smoke = []

    def _parse_args(self, arg):
        i = 0
        while i < len(arg):
            if arg[i] == '-':
                i += 1
                while i < len(arg) and arg[i] != '-':
                    c = arg[i]
                    if c == 'l':
                        self.LOGO += 1
                    elif c == 'a':
                        self.ACCIDENT = 1
                    elif c == 'F':
                        self.FLY = 1
                    elif c == 'c':
                        self.C51 = 1
                    elif c == 'd':
                        self.DANCE = 1
                    elif c == 'r':
                        self.RAND = 1
                    i += 1
            else:
                i += 1

    def _count_frames(self):
        if self.LOGO >= 1:
            return -(-84 - 21 * (self.LOGO - 1) - 1) + self.COLS - 1
        elif self.C51 == 1:
            return -(-87 - 1) + self.COLS - 1
        else:
            return -(-83 - 1) + self.COLS - 1

    def _draw_string(self, buf, y, x, s):
        if y < 0 or y >= self.LINES:
            return
        col = 0
        while col < len(s) and x + col < 0:
            col += 1
        while col < len(s) and x + col < self.COLS:
            buf[y][x + col] = s[col]
            col += 1

    def _output_frame(self, buf):
        lines = []
        for y in range(self.LINES):
            lines.append(''.join(buf[y]))
        return '\n'.join(lines)

    def _add_man(self, buf, y, x):
        frame = (LOGOLENGTH + x) // 12 % 2
        for i in range(2):
            self._draw_string(buf, y + i, x, MAN[frame][i])

    def _add_mdancer(self, buf, y, x):
        frame = (LOGOLENGTH + x) // 12 % 3
        for i in range(3):
            self._draw_string(buf, y + i, x + 1, EMDANCER[frame][i])
            self._draw_string(buf, y + i, x, MDANCER[frame][i])

    def _add_fdancer(self, buf, y, x):
        frame = (LOGOLENGTH + x) // 12 % 2
        for i in range(3):
            self._draw_string(buf, y + i, x + 1, EFDANCER[frame][i])
            self._draw_string(buf, y + i, x, FDANCER[frame][i])

    def _add_smoke(self, buf, y, x):
        if x % 4 == 0:
            for p in self._smoke:
                p[1] += SMOKE_DX[p[2]]
                p[0] -= SMOKE_DY[p[2]]
                if p[2] < SMOKEPTNS - 1:
                    p[2] += 1
            kind = len(self._smoke) % 2
            self._smoke.append([y, x, 0, kind])
        for p in self._smoke:
            self._draw_string(buf, p[0], p[1],
                              (SMOKE1 if p[3] else SMOKE0)[p[2]])

    def _add_sl(self, buf, x):
        offset = 21
        y = self.LINES // 2 - 3
        py1 = 0
        py2 = 0
        py3 = 0
        if self.FLY:
            y = (x // 6) + self.LINES - (self.COLS // 6) - LOGOHEIGHT
            py1 = 2
            py2 = 4
            py3 = 6
        for i in range(LOGOHEIGHT + 1):
            pat_idx = (LOGOLENGTH + offset * (self.LOGO - 1) + x) // 3 % LOGOPATTERNS
            self._draw_string(buf, y + i, x,
                              LOGO_SL_PATTERNS[pat_idx][i])
            self._draw_string(buf, y + i + py1, x + 21, LOGO_COAL[i])
            for j in range(self.LOGO + 1):
                yoff = 2 * j * (1 if self.FLY else 0)
                self._draw_string(buf, y + i + py3 + yoff,
                                  x + 42 + offset * j, LOGO_CAR[i])
        if self.ACCIDENT:
            self._add_man(buf, y + 1, x + 14)
            for j in range(self.LOGO + 1):
                yoff = (1 if self.FLY else 0) * (2 + 2 * j)
                self._add_man(buf, y + 1 + py2 + yoff, x + 45 + offset * j)
                self._add_man(buf, y + 1 + py2 + yoff, x + 53 + offset * j)
        if self.DANCE and not self.ACCIDENT and not self.FLY:
            self._add_mdancer(buf, y - 2, x + 21)
            for j in range(self.LOGO + 1):
                self._add_mdancer(buf, y + py2 - 2, x + 45 + offset * j)
                self._add_mdancer(buf, y + py2 - 2, x + 50 + offset * j)
                self._add_mdancer(buf, y + py2 - 2, x + 55 + offset * j)
        self._add_smoke(buf, y - 1, x + LOGOFUNNEL)

    def _add_D51(self, buf, x):
        y = self.LINES // 2 - 5
        dy = 0
        if self.FLY:
            y = (x // 7) + self.LINES - (self.COLS // 7) - D51HEIGHT
            dy = 1
        for i in range(D51HEIGHT + 1):
            pat_idx = (D51LENGTH + x) % D51PATTERNS
            self._draw_string(buf, y + i, x, D51_PATTERNS[pat_idx][i])
            self._draw_string(buf, y + i + dy, x + 53, D51_COAL[i])
        if self.ACCIDENT:
            self._add_man(buf, y + 2, x + 43)
            self._add_man(buf, y + 2, x + 47)
        if self.DANCE and not self.ACCIDENT and not self.FLY:
            self._add_mdancer(buf, y - 2, x + 43)
            self._add_fdancer(buf, y - 2, x + 48)
        self._add_smoke(buf, y - 1, x + D51FUNNEL)

    def _add_C51(self, buf, x):
        y = self.LINES // 2 - 5
        dy = 0
        if self.FLY:
            y = (x // 7) + self.LINES - (self.COLS // 7) - C51HEIGHT
            dy = 1
        for i in range(C51HEIGHT + 1):
            pat_idx = (C51LENGTH + x) % C51PATTERNS
            self._draw_string(buf, y + i, x, C51_PATTERNS[pat_idx][i])
            self._draw_string(buf, y + i + dy, x + 55, C51_COAL[i])
        if self.ACCIDENT:
            self._add_man(buf, y + 3, x + 45)
            self._add_man(buf, y + 3, x + 49)
        if self.DANCE and not self.ACCIDENT and not self.FLY:
            self._add_mdancer(buf, y - 1, x + 45)
            self._add_fdancer(buf, y - 1, x + 50)
        self._add_smoke(buf, y - 1, x + C51FUNNEL)

    def _map_modify(self, buf, mod):
        x = -mod + self.COLS - 1
        if self.LOGO >= 1:
            self._add_sl(buf, x)
        elif self.C51 == 1:
            self._add_C51(buf, x)
        else:
            self._add_D51(buf, x)

    def step(self, frame):
        if frame >= self.N:
            return None
        buf = [[' '] * self.COLS for _ in range(self.LINES)]
        self._map_modify(buf, frame)
        return self._output_frame(buf)


def sl(cols, lines, arg=""):
    engine = _Engine(cols, lines, arg)
    for frame in range(engine.N):
        yield engine.step(frame)
