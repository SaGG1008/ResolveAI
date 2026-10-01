@echo off
echo ===================================================
echo Starting ResolveAI (Backend FastAPI + Frontend Vite)
echo ===================================================

start "ResolveAI Backend" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"
start "ResolveAI Frontend" cmd /k "cd frontend && npm run dev"

echo Backend running on http://localhost:8000/docs
echo Frontend running on http://localhost:5173
