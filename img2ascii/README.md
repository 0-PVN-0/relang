# img2ascii

JPEG/PNG image to ASCII art converter.

| Field | Value |
|-------|-------|
| **Type** | Easy |
| **Score** | 100 |
| **Reference** | C |

## Prerequisites

- GCC

## Build

```bash
gcc -o /tmp/img2ascii img2ascii/source/src/main.c -Wall -Wextra -lm
```

## Run

```bash
/tmp/img2ascii -i <image-file> -w <width> -p
```

Example:
```bash
/tmp/img2ascii -i img2ascii/source/images/c.png -w 40 -p
```

## Validate

Volunteer-verified — demonstrate the program working during review.

## Submit

```bash
source setup.sh
relang "/tmp/img2ascii"
```
