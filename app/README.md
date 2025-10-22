# Bird Identification Desktop App

## Local development 
```
python3.9 -m venv env
source env/bin/activate
pip install -e .. --config-settings editable_mode=compat # install scripts in editable mode, editable_mode=compat is needed for pyinstaller to work
pip install -r requirements.txt
./start-dev.sh
```
### Compile resources after making changes to icons or style files:
```
pyside6-rcc resources.qrc -o resources.py
```

## Build app
```
pyinstaller app.spec
```