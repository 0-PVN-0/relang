# marked — Test Suite

Markdown to HTML processor

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
  "data": "...input content...",
  "timeout": 30
}
```

- `type`: `"stdin"` — pipe `data` to tool's stdin, or `"file"` — write `data` to a temp file and pass path as argument
- `data`: the raw input your tool should process
- `timeout`: max seconds for execution

## Expected output format (`output/{id}.json`)

```json
{
  "id": "test_001",
  "output": "...expected stdout..."
}
```

## How to test locally

```bash
python validate.py "<your-tool-command>"
```

Examples:

```bash
# Node.js tool
python validate.py "node marked.js"

# Python tool
python validate.py "python3 my_impl.py"

# Compiled binary
python validate.py "./my-parser"

# With arguments
python validate.py "java -jar parser.jar"
```

The script runs your tool against every test case, hashes the output, and compares against the expected hash. Pass/fail per test is printed, with a summary at the end.

## Test selection

This folder contains **1052/4215 test cases** (24% of the full suite). Use `build_deliverables.py --percent N` to regenerate with a different percentage.

## Hash-based comparison

Output correctness is verified by **SHA256 hash comparison**, not direct text diff. Your tool must produce **byte-identical** output to the reference implementation. This is deterministic across languages for the same input.
