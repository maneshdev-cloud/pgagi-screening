#!/bin/bash
# Start backend (8000) and frontend (3000) for a local demo.
set -e
cd "$(dirname "$0")/.."
(cd backend && ./venv/bin/uvicorn app.main:app --port 8000 &)
(cd frontend && npm run dev)
