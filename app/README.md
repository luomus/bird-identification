# Bird Identification Desktop App

## Development


1. Setup virtual environment
    ```
    python3.9 -m venv env
    source env/bin/activate # (or .\env\Scripts\activate in Windows)
    ```

2. Install scripts in editable mode, the option editable_mode=compat is needed for pyinstaller to work. If this command fails, upgrade pip to a newer version
    ```
    pip install -e .. --config-settings editable_mode=compat
    ```

3. Install dependencies specific to the desktop app
    ```
    pip install -r requirements.txt
    ```

4. Start the app
    ```
    ./start-dev.sh # restarts the app automatically when *.py files change
    ```
   or
    ```
    python app.py
    ```

### Compile resources after making changes to icons or style files:
```
pyside6-rcc resources.qrc -o resources.py
```

## Build app
```
pyinstaller app.spec
```
