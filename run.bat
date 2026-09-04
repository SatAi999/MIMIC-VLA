@echo off
echo ================================================================
echo    MIMIC-VLA — Autonomous Embodied AI Control Center
echo ================================================================
echo.

set PYTHON_EXE=D:\Computer_Vision\venv\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment python executable not found at %PYTHON_EXE%
    pause
    exit /b 1
)

echo [1/3] Running pre-flight unit tests...
"%PYTHON_EXE%" -m pytest tests/
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Unit tests failed! Please resolve issues before launching.
    pause
    exit /b 1
)
echo [✓] Pre-flight unit tests passed!

echo.
echo [2/3] Starting MIMIC-VLA Core FastAPI Server...
echo [✓] Dashboard available at: http://localhost:8000
echo.

"%PYTHON_EXE%" main.py
