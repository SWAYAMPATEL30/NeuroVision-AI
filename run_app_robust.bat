@echo off
echo Starting Medical Classification App (Robust Mode)...
echo.

:restart
echo [%date% %time%] Starting Streamlit app...
cd /d "%~dp0"
python -m streamlit run app_specialized.py --server.port 8502 --server.headless true

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] App crashed with exit code %errorlevel%
    echo Waiting 5 seconds before restart...
    timeout /t 5 /nobreak >nul
    echo Restarting...
    goto restart
) else (
    echo.
    echo [INFO] App stopped normally
    pause
)


