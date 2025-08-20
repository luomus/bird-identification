# PowerShell script for building Bird Identification MVP on Windows
# Run this from the project root directory

Write-Host "Building Bird Identification MVP for Windows..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.9+ and add it to PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "app\main.py")) {
    Write-Host "ERROR: Please run this script from the project root directory." -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if models exist
if (-not (Test-Path "models\model_v3_5.keras")) {
    Write-Host "ERROR: Missing model file: models\model_v3_5.keras" -ForegroundColor Red
    Write-Host "Please ensure the required model files are in the ./models directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Test-Path "models\BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite")) {
    Write-Host "ERROR: Missing model file: models\BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite" -ForegroundColor Red
    Write-Host "Please ensure the required model files are in the ./models directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv-windows
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv-windows\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install -U pip wheel setuptools
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to upgrade pip." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install -r app\requirements-windows-x64.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
python -m pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install PyInstaller." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Building application..." -ForegroundColor Yellow
python -m PyInstaller --clean app\pyinstaller-windows-x64.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "The application is located in: dist\BirdIdentification-MVP\" -ForegroundColor Green
Write-Host ""
Write-Host "To run the app:" -ForegroundColor Cyan
Write-Host "1. Navigate to dist\BirdIdentification-MVP\" -ForegroundColor White
Write-Host "2. Double-click BirdIdentification-MVP.exe" -ForegroundColor White
Write-Host ""
Write-Host "To distribute the app:" -ForegroundColor Cyan
Write-Host "1. Zip the entire dist\BirdIdentification-MVP\ folder" -ForegroundColor White
Write-Host "2. Share the zip file with others" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
