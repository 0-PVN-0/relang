# pipes

Animated pipes terminal screensaver with Unicode box-drawing characters.

| Field | Value |
|-------|-------|
| **Type** | Easy |
| **Score** | 100 |
| **Reference** | Python |

## Prerequisites

- Python 3.10+

## Build

No build required — it's a Python package.

## Run

```bash
PYTHONPATH=pipes/source/src python3 -m pipes
```

## Validate

Volunteer-verified — demonstrate the program working during review.

## Submit

```bash
source ../setup.sh
relang "python3 -c \"import sys; sys.path.insert(0, 'source/src'); from pipes.__main__ import main; main()\""
```
