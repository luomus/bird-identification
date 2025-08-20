@echo off
REM Conda-based Windows build script for Bird Identification MVP
REM Run this from the project root directory

echo Building Bird Identification MVP for Windows using Conda...

REM Check if conda is available
conda --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Conda not found. Please install Miniconda or Anaconda.
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
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

echo Creating Conda environment...
conda env create -f app\requirements-conda-minimal.yml
if errorlevel 1 (
    echo ERROR: Failed to create Conda environment.
    pause
    exit /b 1
)

echo Activating Conda environment...
call conda activate bird-id-windows
if errorlevel 1 (
    echo ERROR: Failed to activate Conda environment.
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
