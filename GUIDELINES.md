# reLang — Language Migration Hackathon

Port reference programs from one language to any language of your choice. Place your implementation in the `target/` folder of each project.

## Project Table

| Program | Reference Language | Difficulty | Score | Description | Language Restriction |
|---------|-------------------|-----------|-------|-------------|---------------------|
| asciiquarium | Perl | Easy | 100 | ASCII aquarium / sea animation in terminal | Any language |
| cowsay | Perl | Easy | 100 | Configurable talking cow with message display | Any language |
| donut | Python | Easy | 100 | ASCII art rotating donut animation | Any language |
| kilo | C | Easy | 200 | Minimal text editor in under 1K lines | Any language |
| sl | C | Easy | 100 | Steam locomotive running across terminal | Any language |
| qrterminal | Go | Easy | 100 | QR code generator for the terminal | Any language |
| pipes | Python | Easy | 100 | Animated pipes terminal screensaver with Unicode box-drawing | Any language |
| img2ascii | C | Easy | 100 | JPEG image to ASCII art converter | Any language |
| matrix | Python | Easy | 100 | Matrix digital rain terminal effect | Any language |
| tclock | Go | Easy | 100 | Terminal clock with analog/digital modes, countdown, and tailing | Any language |
| picoc | C | Medium | 400 | C interpreter (subset of the language) | Any language |
| marked | JavaScript | Medium | 400 | Markdown to HTML processor | Any language |
| monocypher | C | Medium | 400 | Cryptographic library (Monocypher port) | Any language |
| wren | C | Medium | 400 | Wren programming language interpreter | Any language |
| healthchecks | Python / Django | Hard | 800 | Uptime monitoring web server (HTTP replay) | Any language |

## Difficulty Tiers

| Tier | Score | Verification Method |
|------|-------|-------------------|
| Easy | 100–200 | Volunteer-verified (no auto tests; submit via PR review) |
| Medium | 400 | Automated test suite with SHA256 hash comparison |
| Hard | 800 | Automated test suite (full HTTP replay + validation) |

## Originality Requirements

- **No copying** the reference code from `source/`
- **No thin wrappers** around the original program (e.g. calling the reference binary from your code)
- **No trivial language swaps** — JS↔TS and C↔C++ are not allowed; the spirit is cross-language migration
- **No wrapping** an existing package/library that already implements the functionality

## Allowed Languages

Only the following languages are permitted:

1. Python
2. JavaScript (Node.js, Deno, Bun)
3. TypeScript (JS↔TS and TS↔JS migrations are not allowed)
4. Java
5. C
6. C++
7. C#
8. Go
9. Rust
10. Zig
11. Kotlin
12. Swift
13. Dart
14. Elixir
15. Lua

**C→C++, C++→C, JS→TS, and TS→JS are all considered trivial swaps and are not allowed.** See [Originality Requirements](#originality-requirements).

If your chosen language requires a runtime, include clear instructions for installing it. The project must run on Linux (deliverables are tested on Ubuntu 24.04).

## Submission

1. Place your implementation in `target/` with clear build/run instructions
2. Source the setup script: `source setup.sh` (Linux)
3. Run: `relang <your-program-command>`
4. For Easy projects (volunteer-verified): submit via GitHub PR to the repo

## Verification

- **Easy**: Manual review by a volunteer — you demonstrate the program working
- **Medium/Hard**: Automated — `validate.py` runs your program against test cases and compares SHA256 hashes

## Scoring

- Score is based on percentage of test cases passed
- Higher pass rates yield exponentially more points
- Leaderboard updates live during the event
- Final winners are determined from submitted GitHub repos

## Important Notes

- Do **not** modify `relang-submit.py`, `tester.py`, or `validate.py`
- You are responsible for verifying your own code — AI hallucinations and bugs are on you
- Push the **entire repo** (including source, target, and all project files) to your **private GitHub** and add **nsdcmec** as collaborator
