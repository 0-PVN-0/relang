# tclock

Terminal clock with analog/digital modes, countdown, and tailing.

| Field | Value |
|-------|-------|
| **Type** | Easy |
| **Score** | 100 |
| **Reference** | Go |

## Prerequisites

- Go 1.21+

## Build

```bash
cd tclock/source && go build -o /tmp/tclock .
```

## Run

```bash
/tmp/tclock
```

Options:
- `-analog` — analog clock mode
- `-aa` — anti-aliased analog mode
- `-24` — 24-hour format
- `-countdown 5m` — countdown mode

## Validate

Volunteer-verified — demonstrate the program working during review.

## Submit

```bash
source setup.sh
relang "/tmp/tclock"
```
