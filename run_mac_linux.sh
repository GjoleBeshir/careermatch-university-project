#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
docker compose up -d
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m scripts.wait_for_db
.venv/bin/python -m scripts.seed
.venv/bin/python -m uvicorn app.main:app --reload
