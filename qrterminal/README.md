# qrterminal

QR code generator for the terminal.

| Field | Value |
|-------|-------|
| **Type** | Easy |
| **Score** | 100 |
| **Reference** | Go |

## Prerequisites

- Go 1.21+

## Build

```bash
cd qrterminal/source && go build -o /tmp/qrterminal ./cmd/qrterminal
```

## Run

```bash
/tmp/qrterminal "https://example.com"
```

## Validate

Volunteer-verified — demonstrate the program working during review.

## Submit

```bash
source setup.sh
relang "/tmp/qrterminal"
```
