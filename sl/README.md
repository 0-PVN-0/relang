# sl

Steam locomotive running across your terminal.

| Field | Value |
|-------|-------|
| **Type** | Easy |
| **Score** | 100 |
| **Reference** | Python/C |

## Prerequisites

- Python 3.8+
- GCC (for C extension build)

## Build

```bash
cd sl/source && python3 setup.py build_ext --inplace
```

## Run

```bash
cd sl/source && python3 -c "from slpy.command_line import main; main()"
```

## Validate

Volunteer-verified — demonstrate the program working during review.

## Submit

```bash
source ../setup.sh
relang "python3 -c \"import sys; sys.path.insert(0, 'source'); from slpy.command_line import main; main()\""
```
