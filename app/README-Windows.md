# Building and Running on Windows

## Prerequisites

1. **Python 3.9+** installed and added to PATH
2. **Git** (to clone the repository)
3. **Required model files** in the `./models` directory:
   - `model_v3_5.keras`
   - `BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite`

## Quick Build (Automated)

1. **Clone and navigate to the project:**
   ```cmd
   git clone <your-repo-url>
   cd bird-identification
   ```

2. **Run the automated build script:**
   ```cmd
   app\build-windows.bat
   ```

   This script will:
   - Create a virtual environment
   - Install all dependencies
   - Build the app with PyInstaller
   - Place the result in `dist\BirdIdentification-MVP\`

## Manual Build Steps

If you prefer to build manually or the automated script fails:

1. **Create virtual environment:**
   ```cmd
   python -m venv .venv-windows
   .venv-windows\Scripts\activate.bat
   ```

2. **Install dependencies:**
   ```cmd
   python -m pip install -U pip wheel setuptools
   python -m pip install -r app\requirements-windows-x64.txt
   ```

3. **Install PyInstaller:**
   ```cmd
   python -m pip install pyinstaller
   ```

4. **Build the app:**
   ```cmd
   python -m PyInstaller --clean app\pyinstaller-windows-x64.spec
   ```

## Running the App

1. **Navigate to the built app:**
   ```cmd
   cd dist\BirdIdentification-MVP
   ```

2. **Run the executable:**
   ```cmd
   BirdIdentification-MVP.exe
   ```

   Or double-click `BirdIdentification-MVP.exe` in File Explorer

## What Gets Built

The build creates a folder `dist\BirdIdentification-MVP\` containing:

- `BirdIdentification-MVP.exe` - Main application
- `models/` - AI model files
- `scripts/` - Required data files
- All Python dependencies and DLLs
- Optional: `ffmpeg/` if you bundle ffmpeg binaries

## Bundling FFmpeg (Optional)

To include ffmpeg for better audio format support:

1. **Download ffmpeg for Windows:**
   - Go to https://ffmpeg.org/download.html
   - Download Windows builds (choose "Windows builds from gyan.dev")
   - Extract and get `ffmpeg.exe` and `ffprobe.exe`

2. **Place in the app resources:**
   ```
   app\resources\ffmpeg\windows-x64\
   ├── ffmpeg.exe
   └── ffprobe.exe
   ```

3. **Rebuild the app** using the steps above

## Troubleshooting

### "Python not found" error
- Ensure Python is installed and added to PATH
- Try running `python --version` in Command Prompt

### Missing model files
- Verify `./models/` contains the required `.keras` and `.tflite` files
- Check file permissions

### Build fails with PyInstaller
- Ensure you're in the project root directory
- Try updating pip: `python -m pip install -U pip`
- Check if antivirus is blocking the build process

### App crashes on startup
- Check Windows Event Viewer for error details
- Ensure all required DLLs are present in the dist folder
- Try running from Command Prompt to see error messages

## Distribution

To share the app with others:

1. **Zip the entire `dist\BirdIdentification-MVP\` folder**
2. **Share the zip file**
3. **Recipients extract and run `BirdIdentification-MVP.exe`**

The app is self-contained and doesn't require Python installation on target machines.

## File Structure After Build

```
dist\BirdIdentification-MVP\
├── BirdIdentification-MVP.exe
├── models\
│   ├── model_v3_5.keras
│   └── BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite
├── scripts\
│   ├── classes.csv
│   └── Pred_adjustment\
│       └── calibration_params.npy
├── app\resources\ffmpeg\windows-x64\  (if bundled)
│   ├── ffmpeg.exe
│   └── ffprobe.exe
└── [Python dependencies and DLLs]
```
