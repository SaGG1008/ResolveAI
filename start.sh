#!/bin/bash
echo "==================================================="
echo "Starting ResolveAI (Backend FastAPI + Frontend Vite)"
echo "==================================================="

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd frontend && npm run dev &
FRONTEND_PID=$!

echo "Backend running on http://localhost:8000/docs"
echo "Frontend running on http://localhost:5173"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
