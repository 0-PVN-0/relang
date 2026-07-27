# monocypher — Test Suite

Cryptographic library (Monocypher port)

## Contents

| File/Dir | Purpose |
|---|---|
| `input/` | Test input files (`.json`), one per test case |
| `output/` | Expected output files (`.json`), one per test case |
| `project_config.json` | Project metadata: input type, name, ID |
| `validate.py` | Local test runner — run your tool against the test suite |
| `tester.py` | CLI adapter — receives batch via stdin, outputs results |

## Test case format (`input/{id}.json`)

```json
{
  "id": "test_001",
  "type": "stdin",
  "data": "crypto_chacha20_djb\n95b95da31991388777c9a2bffa604831edc2909eee8c06cb217cc4d4f4f17573:\n5dab69dc52cc8221:\n...",
  "timeout": 30
}
```

- `type`: `"stdin"` — pipe `data` to tool's stdin as-is
- `data`: the stdin protocol: function name on first line, then each hex parameter followed by `:` on its own line
- `timeout`: max seconds for execution

## Stdin/stdout protocol

Your CLI must read from stdin and write to stdout using this hex protocol:

**Input format** (one test case):
```
crypto_chacha20_djb
95b95da31991388777c9a2bffa604831edc2909eee8c06cb217cc4d4f4f17573:
5dab69dc52cc8221:
```

**Output format**:
```
c0d97ecb00058d030cc86603014efd7ddc19f464a49a394036ee7b198a7b81777:
```

Each input parameter is a hex-encoded byte string, terminated by `:`. Each output is also hex-encoded and `:`-terminated.

## Expected output format (`output/{id}.json`)

```json
{
  "id": "test_001",
  "output": "c0d97ecb00058d030cc86603014efd7ddc19f464a49a394036ee7b198a7b81777:\n"
}
```

## How to test locally

```bash
python validate.py "<your-tool-command>"
```

Examples:

```bash
# Compiled C port
python validate.py "./monocypher-cli"

# Rust port via cargo
python validate.py "cargo run --release --"

# Python port
python validate.py "python3 monocypher.py"
```

The script runs your tool against every test case, hashes the output, and compares against the expected hash. Pass/fail per test is printed, with a summary at the end.

## Test selection

This folder contains **939/3735 test cases** (25% of the full suite). Use `build_deliverables.py --percent N` to regenerate with a different percentage.

## Hash-based comparison

Output correctness is verified by **SHA256 hash comparison**, not direct text diff. Your tool must produce **byte-identical** output to the reference C implementation (monocypher-cli). This is deterministic across languages for the same inputs.
