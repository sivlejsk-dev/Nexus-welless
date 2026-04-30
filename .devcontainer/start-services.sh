#!/usr/bin/env bash
# Start backend and frontend on environment boot

set -e

# Backend
cd /workspaces/workspaces/backend
source venv/bin/activate 2>/dev/null || true
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
echo "Backend starting (PID $!)"

# Frontend
cd /workspaces/workspaces/frontend
nohup npm run dev -- --port 3000 > /tmp/frontend.log 2>&1 &
echo "Frontend starting (PID $!)"

echo "Services launched. Logs: /tmp/backend.log and /tmp/frontend.log"
