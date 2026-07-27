# healthchecks

Uptime monitoring web server (Django). Supports HTTP replay-based testing.

| Field | Value |
|-------|-------|
| **Type** | Hard |
| **Score** | 800 |
| **Reference** | Python/Django |

## Prerequisites

Your target language toolchain (whatever your implementation needs).

## Run

Run your implementation in `target/` on the appropriate port. For example:

```bash
<your-program-command>
```

Replace `<your-program-command>` with the command to run your implementation in `target/`.

## Validate (local)

With server running at the appropriate URL:

```bash
cd healthchecks/relang && python3 validate.py <your-server-url>
```

## Submit

```bash
source ../setup.sh
relang "<your-server-url>"
```

> ⚠️ **Do NOT submit the source reference implementation.**  
> Only implement and submit your code from `target/`.  
> Submitting `source/` may result in **disqualification**.
