#!/bin/bash
# =============================================================================
# SWAYAMSEM — Run Streamlit UI (use after setup.sh)
# =============================================================================
# Run from project root. Activates venv if present, then starts Streamlit.
#   ./run.sh         → Streamlit on port 8502
#   ./run.sh api     → REST API on port 8000
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    if [ -f "$VENV_DIR/bin/activate" ]; then
        # shellcheck disable=SC1091
        . "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        # shellcheck disable=SC1091
        . "$VENV_DIR/Scripts/activate"
    fi
fi

MODE="${1:-ui}"
if [ "$MODE" = "api" ]; then
    echo "Starting REST API on http://localhost:8000 ..."
    echo "Docs: http://localhost:8000/docs"
    exec python -m uvicorn api:app --reload --port 8000
else
    echo "Starting Streamlit UI on http://localhost:8502 ..."
    exec python -m streamlit run app_specialized.py --server.port 8502 --server.headless true
fi
