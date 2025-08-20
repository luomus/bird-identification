@echo off
REM Automated Windows build script for Bird Identification MVP
REM Run this from the project root directory

echo Building Bird Identification MVP for Windows...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "app\main.py" (
    echo ERROR: Please run this script from the project root directory.
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if models exist
if not exist "models\model_v3_5.keras" (
    echo ERROR: Missing model file: models\model_v3_5.keras
    echo Please ensure the required model files are in the ./models directory.
    pause
    exit /b 1
)

if not exist "models\BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite" (
    echo ERROR: Missing model file: models\BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite
    echo Please ensure the required model files are in the ./models directory.
    pause
    exit /b 1
)

echo Creating virtual environment...
python -m venv .venv-windows
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv-windows\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Upgrading pip...
python -m pip install -U pip wheel setuptools
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip.
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install -r app\requirements-windows-x64.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo Building application...
python -m PyInstaller --clean app\pyinstaller-windows-x64.spec
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo.
echo The application is located in: dist\BirdIdentification-MVP\
echo.
echo To run the app:
echo 1. Navigate to dist\BirdIdentification-MVP\
echo 2. Double-click BirdIdentification-MVP.exe
echo.
echo To distribute the app:
echo 1. Zip the entire dist\BirdIdentification-MVP\ folder
echo 2. Share the zip file with others
echo.

REM Keep console open
pause
