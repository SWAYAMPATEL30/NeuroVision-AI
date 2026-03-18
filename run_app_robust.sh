#!/bin/bash
# Robust Streamlit app runner - auto-restarts on crash

echo "Starting Medical Classification App (Robust Mode)..."

cd "$(dirname "$0")"

while true; do
    echo "[$(date)] Starting Streamlit app..."
    python -m streamlit run app_specialized.py --server.port 8502 --server.headless true
    
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "[ERROR] App crashed with exit code $EXIT_CODE"
        echo "Waiting 5 seconds before restart..."
        sleep 5
        echo "Restarting..."
    else
        echo ""
        echo "[INFO] App stopped normally"
        break
    fi
done


