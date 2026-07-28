// sl - Steam Locomotive in Go
// Ported from sl.c (Perl -> Go)
// Copyright 1993,1998,2014 Toyoda Masashi

package main

import (
	"fmt"
	"os"
	"strings"
	"time"
)

// ANSI escape codes for terminal control
const (
	ESC = "\x1b["
)

// Terminal dimensions
var (
	cols, lines int
)

// Flags from command line options
var (
	ACCIDENT = 0
	LOGO     = 0
	FLY      = 0
	C51      = 0
	DANCE    = 0
	RAND     = 0
)

// D51 train constants
const (
	d51Height   = 10
	d51Funnel   = 7
	d51Length   = 83
	d51Patterns = 6
)

// D51 train string patterns
var d51Str = []string{
	"      ====        ________                ___________ ",
	"  _D _|  |_______/        \\__I_I_____===__|_________| ",
	"   |(_)---  |   H\\________/ |   |        =|___ ___|   ",
	"   /     |  |   H  |  |     |   |         ||_| |_||   ",
	"  |      |  |   H  |__--------------------| [___] |   ",
	"  | ________|___H__/__|_____/[][]~\\_______|       |   ",
	"  |/ |   |-----------I_____I [][] []  D   |=======|__ ",
}

var d51Whl = [][]string{
	{"__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ", " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ", "  \\_/      \\O=====O=====O=====O_/      \\_/            "},
	{"__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ", " |/-=|___|=O=====O=====O=====O   |_____/~\\___/        ", "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "},
	{"__/ =| o |=-O=====O=====O=====O \\ ____Y___________|__ ", " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ", "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "},
	{"__/ =| o |=-~O=====O=====O=====O\\ ____Y___________|__ ", " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ", "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "},
	{"__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ", " |/-=|___|=   O=====O=====O=====O|_____/~\\___/        ", "  \\_/      \\__/  \\__/  \\__/  \\__/      \\_/            "},
	{"__/ =| o |=-~~\\  /~~\\  /~~\\  /~~\\ ____Y___________|__ ", " |/-=|___|=    ||    ||    ||    |_____/~\\___/        ", "  \\_/      \\_O=====O=====O=====O/      \\_/            "},
}

var d51Del = "                                                      "

// Coal patterns
var coal = []string{
	"                              ",
	"                              ",
	"    _________________         ",
	"   _|                \\_____A  ",
	" =|                        |  ",
	" -|                        |  ",
	" __|________________________|_ ",
	"|__________________________|_ ",
	"   |_D__D__D_|  |_D__D__D_|   ",
	"    \\_/   \\_/    \\_/   \\_/    ",
}

var coalDel = "                              "

// Output buffer
var outputMap []string

// Count for animation frames
var animCount int

func init() {
	// Get terminal size - default to 80x24
	cols, lines = 80, 24
}

func count() int {
	min := 0
	offset := 21
	if LOGO >= 1 {
		min = -6 - 1 - offset*(LOGO-1) // LOGOHEIGHT = 6
	} else if C51 == 1 {
		min = -11 - 1 // C51HEIGHT = 11
	} else {
		min = -10 - 1 // D51HEIGHT = 10
	}
	return min
}

func addChModify(y, x int, c rune) {
	if y < 0 || x < 0 || x >= cols || y >= lines {
		return
	}
	outputMap[y] = outputMap[y][:x] + string(c) + outputMap[y][x+1:]
}

func myMvaddstr(y, x int, str string) {
	for x < 0 {
		x++
		if len(str) == 0 {
			return
		}
		str = str[1:]
	}
	for _, c := range str {
		if x >= cols {
			return
		}
		addChModify(y, x, c)
		x++
	}
}

func option(str string) {
	for len(str) > 0 && str[0] != '-' {
		switch str[0] {
		case 'l':
			LOGO++
		case 'a':
			ACCIDENT = 1
		case 'F':
			FLY = 1
		case 'c':
			C51 = 1
		case 'd':
			DANCE = 1
		case 'r':
			RAND = 1
		}
		str = str[1:]
	}
}

func windowInit(c, l int, arg string) {
	cols = c
	lines = l

	ACCIDENT = 0
	LOGO = 0
	FLY = 0
	C51 = 0
	DANCE = 0
	RAND = 0

	for len(arg) > 0 {
		if arg[0] == '-' {
			option(arg[1:])
		}
		arg = arg[1:]
	}

	if RAND == 1 {
		// Simple random for demo
	}

	animCount = -count() + cols - 1

	// Initialize output buffer
	outputMap = make([]string, lines)
	for i := range outputMap {
		outputMap[i] = strings.Repeat(" ", cols)
	}
}

func mapModify(mod int) {
	x := -mod + cols - 1
	if LOGO >= 1 {
		addSL(x)
	} else if C51 == 1 {
		addC51(x)
	} else {
		addD51(x)
	}
}

func addD51(x int) {
	y := lines/2 - 5

	for i := 0; i <= d51Height; i++ {
		patternIdx := (d51Length+x) % d51Patterns
		if patternIdx < len(d51Str) {
			myMvaddstr(y+i, x, d51Str[patternIdx])
		}
		if i < len(coal) {
			myMvaddstr(y+i+1, x+53, coal[i])
		}
	}
	if ACCIDENT == 1 {
		myMvaddstr(y+2, x+43, "(O)")
		myMvaddstr(y+2, x+47, "(O)")
	}
}

func addC51(x int) {
	y := lines/2 - 5

	// Simplified C51 train pattern
	trainStr := []string{
		"        ___                                            ",
		"       _|_|_  _     __       __             ___________",
		"    D__/   \\_(_)___|  |__H__|  |_____I_Ii_()|_________|",
		"     | `---'   |:: `--'  H  `--'         |  |___ ___|  ",
		"    +|~~~~~~~~++::~~~~~~~H~~+=====+~~~~~~|~~||_| |_||  ",
		"    ||        | ::       H  +=====+      |  |::  ...|  ",
		"|    | _______|_::-----------------[][]-----|       |  ",
	}

	yOff := 0
	if FLY == 1 {
		yOff = 1
	}

	for i := 0; i <= 10; i++ {
		patternIdx := (87+x) % 6 // C51LENGTH = 87, C51PATTERNS = 6
		if patternIdx < len(trainStr) {
			myMvaddstr(y+i, x, trainStr[patternIdx])
		}
		if i < len(coal) {
			myMvaddstr(y+i+yOff, x+55, coal[i])
		}
	}
	if ACCIDENT == 1 {
		myMvaddstr(y+3, x+45, "(O)")
		myMvaddstr(y+3, x+49, "(O)")
	}
}

func addMan(y, x int) {
	man := [][]string{
		{"", "(O)"},
		{"Help!", "\\O/"},
	}
	for i := 0; i < 2; i++ {
		myMvaddstr(y+i, x, man[(84+x)/12%2][i]) // LOGOLENGTH = 84
	}
}

func addSmokes(y, x int) {
	// Simplified smoke effect
	smoke := []string{
		"(   )",
		"(    )",
		"(    )",
		"(   )",
		"(  )",
		"(  )",
		"( )",
		"( )",
		"()",
		"()",
		"O",
		"O",
		"O",
		"O",
		"O",
		" ",
	}

	// Add smoke at position
	if x%4 == 0 {
		for i := 0; i < 5; i++ {
			sy := y - i*2 + 1
			sx := x + 4*i - 2
			if sy >= 0 && sy < lines && sx >= 0 && sx < cols {
				if i < len(smoke) {
					myMvaddstr(sy, sx, smoke[i])
				}
			}
		}
	}
}

func addSL(x int) {
	// Logo train patterns
	logoStr := []string{
		"     ++      +------ ",
		"     ||      |+-+ |  ",
		"   /---------|| | |  ",
		"  + ========  +-+ |  ",
	}

	logoCoal := []string{
		"____                 ",
		"|   \\@@@@@@@@@@@     ",
		"|    \\@@@@@@@@@@@@@_ ",
		"|                  | ",
		"|__________________| ",
		"   (O)       (O)     ",
	}

	logoCar := []string{
		"____________________ ",
		"|  ___ ___ ___ ___ | ",
		"|  |_| |_| |_| |_| | ",
		"|__________________| ",
		"|__________________| ",
		"   (O)        (O)    ",
	}

	offset := 21
	y := lines / 2

	if FLY == 1 {
		y = (x / 6) + lines - (cols / 6) - 6
	}

	for i := 0; i <= 6; i++ {
		patternIdx := (84+offset*(LOGO-1)+x)/3%6 // LOGOLENGTH=84, LOGOPATTERNS=6
		if patternIdx < len(logoStr) {
			myMvaddstr(y+i, x, logoStr[patternIdx])
		}
		if i < len(logoCoal) {
			myMvaddstr(y+i, x+21, logoCoal[i])
		}
		for j := 0; j <= LOGO; j++ {
			yoffset := 2 * j * FLY
			if i < len(logoCar) {
				myMvaddstr(y+i+6+yoffset, x+42+offset*j, logoCar[i])
			}
		}
	}
	if ACCIDENT == 1 {
		addMan(y+1, x+14)
		for j := 0; j <= LOGO; j++ {
			yoffset := FLY * (2 + 2*j)
			addMan(y+1+2+yoffset, x+45+offset*j)
			addMan(y+1+2+yoffset, x+53+offset*j)
		}
	}
	addSmokes(y-1, x+4) // LOGOFUNNEL = 4
}

func main() {
	arg := ""
	if len(os.Args) > 1 {
		arg = os.Args[1]
	}

	// Initialize
	windowInit(80, 24, arg)

	// Output the animation
	for i := 0; i < animCount; i++ {
		// Reset output map
		for j := range outputMap {
			outputMap[j] = strings.Repeat(" ", cols)
		}

		mapModify(i)

		// Print the frame
		for _, line := range outputMap {
			fmt.Println(line[:cols])
		}

		time.Sleep(10 * time.Millisecond)
	}
}