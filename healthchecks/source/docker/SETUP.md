# Docker Setup for Healthchecks Reference Server

## Quick Start

```bash
docker compose up --build
```

Server starts on `http://localhost:8000`.

On startup: migrate DB → seed test users (alice/bob/charlie, password: "password") → run dev server.

## Required Env Variables

Set in `docker-compose.yml` — no `.env` file needed:

- `SECRET_KEY=testing-fixed-secret-key-for-both-servers`
- `SITE_ROOT=http://localhost:8000`
- `EMAIL_HOST=localhost` (enables magic-link login form)
- `DEBUG=True`, `ALLOWED_HOSTS=*`, `REGISTRATION_OPEN=True`

## Run Tests

```bash
cd ../relang
python validate.py http://localhost:8000
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Connection refused | `docker compose up` |
| All tests fail | Check port number |
| Stale data | `docker compose down -v && docker compose up --build` |
