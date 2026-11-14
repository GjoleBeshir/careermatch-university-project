#!/bin/sh
set -eu
# Seeds generated fictional records (idempotently), then starts HTTP server.
python -m scripts.wait_for_db
python -m scripts.seed
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-10000}"
