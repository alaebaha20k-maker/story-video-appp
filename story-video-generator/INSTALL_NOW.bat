@echo off
echo ========================================
echo Installing Backend Dependencies
echo ========================================
echo.

REM Upgrade pip first
echo [1/3] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo [2/3] Installing dependencies...
pip install flask flask-cors edge-tts pydub moviepy pillow numpy requests python-dotenv google-generativeai soundfile
echo.

REM Verify installation
echo [3/3] Verifying installation...
python -c "import flask; print('Flask version:', flask.__version__)"
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Now run: python api_server.py
echo.
pause
