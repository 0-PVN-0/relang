# healthchecks — Test Suite

Healthchecks uptime monitoring server

## Contents

| File/Dir | Purpose |
|---|---|
| `input/` | Test input files (`.json`), one per test case |
| `output/` | Expected output files (`.json`), one per test case |
| `project_config.json` | Project metadata: input type, name, ID |
| `validate.py` | Local test runner — replay tests against your server |
| `tester.py` | CLI adapter — receives batch via stdin, outputs results |

## How to test locally

```bash
python validate.py http://localhost:8000
```

## Test selection

This folder contains **134/539 test cases** (24% of the full suite).
