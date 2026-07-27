# reLang — Language Migration Hackathon

## Event Overview

Participants port reference code from `source/` to any language of their choice, placing their implementation in `target/`. A test harness validates correctness via SHA256 hash comparison of outputs.

## Repository Structure

```
deliverables/
├── GUIDELINES.md          # Rules, originality, scoring
├── AGENTS.md              # This file
├── setup.sh               # Source this to use `relang` CLI (Linux)
├── setup.bat              # Run this to use `relang` CLI (Windows)
├── relang-submit.py       # Submission script (fetches tests, submits hashes)
│
├── asciiquarium/          # Easy (100pts)
├── cowsay/                # Easy (100pts)
├── donut/                 # Easy (100pts)
├── kilo/                  # Easy (200pts)
├── sl/                    # Easy (100pts)
├── qrterminal/            # Easy (100pts)
├── pipes/                 # Easy (100pts)
├── img2ascii/             # Easy (100pts)
├── matrix/                # Easy (100pts)
├── tclock/                # Easy (100pts)
├── picoc/                 # Medium (400pts)
├── marked/                # Medium (400pts)
├── monocypher/            # Medium (400pts)
├── wren/                  # Medium (400pts)
└── healthchecks/          # Hard (800pts)
```

Each project contains:
| File / Dir | Purpose |
|------------|---------|
| `README.md` | Build, run, validate, submit instructions |
| `source/` | Reference implementation (do not copy) |
| `target/` | **Your implementation goes here** |
| `relang/` | Test harness (`validate.py`, `tester.py`, test cases) |

## Persistent Setup (one-time install)

Instead of sourcing `setup.sh` every session, run the installer for your OS:

| Platform | Command | Installs To |
|----------|---------|-------------|
| Linux / macOS | `bash install.sh` | `~/.bashrc` / `~/.zshrc` |
| Windows (PowerShell) | `powershell -File install.ps1` | `$PROFILE` |
| Windows (cmd.exe) | `install.bat` | User `PATH` via `setx` |

After running, open a new terminal and use `relang <your-program-command>`.

## Key Files to Read

- **`GUIDELINES.md`** — Rules, scoring, allowed languages, originality requirements
- **`<project>/README.md`** — Build command, run command, how to validate and submit for each project
- **`<project>/relang/README.md`** — Test protocol details (input format, expected output format)

## Project Categories

| Category | Count | Projects | Score Range | Verification |
|----------|-------|----------|-------------|-------------|
| Easy | 10 | asciiquarium, cowsay, donut, kilo, sl, qrterminal, pipes, img2ascii, matrix, tclock | 100–200 | Volunteer-verified (no auto tests) |
| Medium | 4 | picoc, marked, monocypher, wren | 400 | Automated (hash compare) |
| Hard | 1 | healthchecks | 800 | Automated (HTTP replay) |

## How Submission Works

1. Implement the program in `target/` using any allowed language
2. Install the `relang` CLI (one-time): `bash install.sh` (Linux/macOS), `powershell -File install.ps1` (Windows PowerShell), or `install.bat` (Windows cmd)
3. Open a new terminal and run: `relang <your-program-command>`
4. The script fetches test cases from the server, runs them through your program, hashes the outputs, and submits the hashes
5. Leaderboard updates live

## Rules Summary

- **No copying** the reference code from `source/`
- **No thin wrappers** around the original program
- **No JS↔TS or C↔C++ swaps** — must be a genuinely different language
- **No wrapping existing packages** and calling it your implementation
- **No modifying** `relang-submit.py`, `tester.py`, or `validate.py`
- Push the repo to **private GitHub** and add **nsdcmec** as collaborator
- You are responsible for verifying your code — AI hallucinations and bugs are on you

## Scoring

- Based on **number of test cases passed**
- **Exponential curve** — higher pass rates give disproportionately more points
- Live leaderboard during event; final winners from submitted GitHub repo
