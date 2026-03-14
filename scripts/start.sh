#!/usr/bin/env bash
set -e

# Resolve project root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# Check prerequisites
if [ ! -d ".venv" ]; then
    echo "Error: .venv not found. Run: python3 -m venv .venv && pip install -e ."
    exit 1
fi

if [ ! -d "frontend/build" ]; then
    echo "Error: frontend/build not found. Run: cd frontend && npm run build"
    exit 1
fi

source .venv/bin/activate

echo ""
echo "================================"
echo "  NORM Production Mode"
echo "================================"
echo "  Dashboard: http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop"
echo "================================"
echo ""

uvicorn backend.main:app --host 0.0.0.0 --port 8000
