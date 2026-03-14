#!/usr/bin/env bash
set -e

# Resolve project root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# Check prerequisites
if [ ! -d ".venv" ]; then
    echo "Error: .venv not found. Run: python3 -m venv .venv && pip install -e '.[dev]'"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "Error: frontend/node_modules not found. Run: cd frontend && npm install"
    exit 1
fi

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping NORM..."
    [ -n "${BACKEND_PID}" ] && kill "${BACKEND_PID}" 2>/dev/null
    [ -n "${FRONTEND_PID}" ] && kill "${FRONTEND_PID}" 2>/dev/null
    wait 2>/dev/null
    echo "NORM stopped."
}

trap cleanup SIGINT SIGTERM EXIT

# Start backend
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd "${PROJECT_ROOT}"

echo ""
echo "================================"
echo "  NORM Dev Mode"
echo "================================"
echo "  Backend:   http://localhost:8000"
echo "  Dashboard: http://localhost:5173"
echo "  API docs:  http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop"
echo "================================"
echo ""

# Wait for either process to exit
wait
