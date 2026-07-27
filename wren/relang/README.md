# wren — Test Suite

Wren programming language interpreter

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
  "id": "language/return/in_function",
  "type": "file",
  "data": "var f = Fn.new {\n  return \"ok\"\n  System.print(\"bad\")\n}\n\nSystem.print(f.call()) // expect: ok\n",
  "timeout": 30
}
```

- `type`: `"file"` — write `data` to a temp `.wren` file and pass its path as the program argument
- `data`: the raw Wren source code your interpreter should execute
- `files` (optional): additional files to create alongside the test (for module imports, io data files)
- `timeout`: max seconds for execution

## Expected output format (`output/{id}.json`)

```json
{
  "id": "language/return/in_function",
  "output": "ok\n"
}
```

## How to test locally

```bash
python validate.py "<your-tool-command>"
```

## Hash-based comparison

Output correctness is verified by **SHA256 hash comparison**. Your tool must produce **byte-identical stdout** to the expected output.

## Test selection

This folder contains **452/1811 test cases** (24% of the full suite). Use `build_deliverables.py --percent N` to regenerate.
