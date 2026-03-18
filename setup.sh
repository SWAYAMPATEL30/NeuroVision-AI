#!/bin/bash
# =============================================================================
# SWAYAMSEM / Medical Classifier — One-Click Setup
# =============================================================================
# Run from project root (where medical_classifier.py lives).
#
# Use case: Copy entire project to a new machine/folder, then run:
#   chmod +x setup.sh && ./setup.sh
# or:
#   bash setup.sh
#
# Prerequisites: Python 3.8+ (3.10+ recommended), pip, 10GB+ disk (model cache)
# =============================================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=============================================="
echo "  SWAYAMSEM — One-Click Setup"
echo "=============================================="
echo "  Project dir: $SCRIPT_DIR"
echo "=============================================="
echo ""

# -----------------------------------------------------------------------------
# 1. Check Python
# -----------------------------------------------------------------------------
PY=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")" 2>/dev/null || true)
        if [ -n "$VER" ]; then
            MAJOR=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
            MINOR=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
            if [ "$MAJOR" -ge 3 ] 2>/dev/null && [ "${MINOR:-0}" -ge 8 ] 2>/dev/null; then
                PY="$cmd"
                echo "[1/7] Python: $cmd ($VER)"
                break
            fi
        fi
    fi
done

if [ -z "$PY" ]; then
    echo "[ERROR] Python 3.8+ not found. Install Python 3.10+ and retry."
    exit 1
fi

# -----------------------------------------------------------------------------
# 2. Create virtual environment (if missing)
# -----------------------------------------------------------------------------
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/7] Creating virtual environment: $VENV_DIR"
    "$PY" -m venv "$VENV_DIR"
else
    echo "[2/7] Virtual environment exists: $VENV_DIR"
fi

# Activate venv (bash/zsh)
if [ -f "$VENV_DIR/bin/activate" ]; then
    # shellcheck disable=SC1091
    . "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # Windows-style venv (e.g. Git Bash)
    # shellcheck disable=SC1091
    . "$VENV_DIR/Scripts/activate"
else
    echo "[WARN] Could not find venv activate script. Using system Python."
fi

# -----------------------------------------------------------------------------
# 3. Upgrade pip
# -----------------------------------------------------------------------------
echo "[3/7] Upgrading pip..."
python -m pip install --upgrade pip -q

# -----------------------------------------------------------------------------
# 4. Install main requirements
# -----------------------------------------------------------------------------
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "[ERROR] requirements.txt not found in $SCRIPT_DIR"
    exit 1
fi
echo "[4/7] Installing main dependencies (requirements.txt)..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# -----------------------------------------------------------------------------
# 5. Install API requirements
# -----------------------------------------------------------------------------
if [ -f "$SCRIPT_DIR/requirements_api.txt" ]; then
    echo "[5/7] Installing API dependencies (requirements_api.txt)..."
    pip install -r "$SCRIPT_DIR/requirements_api.txt"
else
    echo "[5/7] requirements_api.txt not found; skipping API deps."
fi

# -----------------------------------------------------------------------------
# 6. Ensure project structure (models dir, etc.)
# -----------------------------------------------------------------------------
echo "[6/7] Checking project structure..."
mkdir -p "$SCRIPT_DIR/major_project-main/models"
[ -f "$SCRIPT_DIR/disease_categories.py" ] || echo "[WARN] disease_categories.py not found; some features may fail."
[ -f "$SCRIPT_DIR/medical_classifier.py" ] || { echo "[ERROR] medical_classifier.py not found."; exit 1; }
[ -f "$SCRIPT_DIR/report_generator.py" ]  || echo "[WARN] report_generator.py not found; PDF reports may fail."

# -----------------------------------------------------------------------------
# 7. Quick verification
# -----------------------------------------------------------------------------
echo "[7/7] Verifying installation..."
python -c "
import sys
err = []
try: import torch
except Exception as e: err.append('torch: ' + str(e))
try: import transformers
except Exception as e: err.append('transformers: ' + str(e))
try: import streamlit
except Exception as e: err.append('streamlit: ' + str(e))
try: import fastapi
except Exception as e: err.append('fastapi: ' + str(e))
try: from PIL import Image
except Exception as e: err.append('PIL: ' + str(e))
if err:
    print('Verification failed:', err)
    sys.exit(1)
print('  torch, transformers, streamlit, fastapi, PIL OK')
" || { echo "[ERROR] Verification failed."; exit 1; }

echo ""
echo "=============================================="
echo "  Setup complete."
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. (Optional) Set HF_TOKEN and GROQ_API_KEY in medical_classifier.py"
echo "     (lines ~46–47) for Hugging Face models and report fallback."
echo ""
echo "  2. Run the app (one-click):"
echo "       chmod +x run.sh && ./run.sh       # Streamlit UI → http://localhost:8502"
echo "       ./run.sh api                      # REST API    → http://localhost:8000/docs"
echo ""
echo "     Or manually:"
echo "       source $VENV_DIR/bin/activate"
echo "       streamlit run app_specialized.py --server.port 8502"
echo "       uvicorn api:app --reload --port 8000"
echo ""
echo "  3. (Optional) Add custom models under major_project-main/models/:"
echo "     - brainTumor.h5, inception_model.h5, resnet_model.h5 (brain)"
echo "     - chest_xray.h5 (chest)"
echo ""
echo "See run.sh for quick run (./run.sh or ./run.sh api)."
echo "=============================================="
echo ""
