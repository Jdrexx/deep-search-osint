# Deep Search OSINT Dashboard

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite)

Passive domain reconnaissance tool: subdomain enumeration, WHOIS lookups, DNS record inspection, and metadata collection. Produces clean investigative reports without actively scanning the target.

## Features

- Domain and company passive search
- WHOIS metadata lookup (registrar, creation date, registrant)
- DNS record inspection (A, AAAA, MX, NS, TXT, CNAME)
- Subdomain discovery via common prefix enumeration
- Report generation in markdown format
- Export findings to file

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8108
```

Open: http://localhost:8108

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Browser demo UI |
| GET | `/api/health` | Health check |
| GET | `/docs` | Interactive API docs |

## Tests

```bash
uv run pytest -q
```
