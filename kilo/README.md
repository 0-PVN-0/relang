# kilo

Minimal text editor in under 1K lines of code.

| Field | Value |
|-------|-------|
| **Type** | Easy |
| **Score** | 200 |
| **Reference** | C |

## Prerequisites

- GCC or any C99 compiler

## Build

```bash
gcc -o /tmp/kilo kilo/source/kilo.c -Wall -W -pedantic -std=c99
```

## Run

```bash
/tmp/kilo <filename>
```

Example:
```bash
/tmp/kilo test.txt
```

## Validate

Volunteer-verified — demonstrate the program working during review.

## Submit

```bash
source setup.sh
relang "/tmp/kilo"
```
