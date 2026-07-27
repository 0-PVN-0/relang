# monocypher

Cryptographic library port (Monocypher) — provides CHACHA20, Poly1305, X25519, Ed25519, and Argon2.

| Field | Value |
|-------|-------|
| **Type** | Medium |
| **Score** | 400 |
| **Reference** | C |

## Prerequisites

Your target language toolchain (whatever your implementation needs).

## Build

Build instructions for your target language implementation in `target/`.

## Run

```bash
<your-program-command>
```

Reads hex-encoded stdin protocol and outputs hex-encoded results.

Replace `<your-program-command>` with the command to run your implementation in `target/`.

## Validate (local)

```bash
cd relang && python3 validate.py "../target/<your-program-command>"
```

## Submit

```bash
source ../setup.sh
relang "<your-program-command>"
```

> ⚠️ **Do NOT submit the source reference implementation.**  
> Only implement and submit your code from `target/`.  
> Submitting `source/` may result in **disqualification**.
