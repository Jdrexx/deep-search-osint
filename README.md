# Deep Search OSINT Dashboard

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite) ![RDAP](https://img.shields.io/badge/RDAP-4A90D9?style=flat-square) ![DNS](https://img.shields.io/badge/DNS-003B57?style=flat-square)

Passive domain reconnaissance: subdomains, WHOIS, DNS records, metadata, and clean investigative reports.

![osint-demo](screenshots/osint-demo.png)

## Features
- Domain/company passive search
- WHOIS metadata lookup
- DNS record inspection
- Report generation (markdown/PDF)
- Export findings to file

## Quick Start

```bash
uv sync
uv run uvicorn src.main:app --reload --port 8108
```

Open: http://localhost:8108

## API
- `GET /` - browser demo
- `GET /api/health` - health check
- `GET /docs` - interactive FastAPI docs

## Verify
```bash
uv run pytest -q
```
