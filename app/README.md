# Bird Identification Desktop App

## Development


1. Setup virtual environment
    ```
    python3.9 -m venv env
    source env/bin/activate # (or .\env\Scripts\activate in Windows)
    ```

2. Install shared package in editable mode, the option editable_mode=compat is needed for pyinstaller to work. If this command fails, upgrade pip to a newer version
    ```
    pip install -e .. --config-settings editable_mode=compat
    ```

3. Install other dependencies
    ```
    pip install -r requirements.txt && pip install -r requirements_tf.txt
    ```
   
4. Add BirdNET model to models folder

5. Start the app
    ```
    ./start-dev.sh # restarts the app automatically when *.py files change
    ```
   or
    ```
    python app.py
    ```

### Compile resources after making changes to icons:
```
pyside6-rcc resources.qrc -o resources.py
```
If you add/delete resources, remember to update file resources.qrc

## Build app
```
pyinstaller app.spec
```

## Run tests
To run tests, you need to have a model in the models folder that can identify something in the test file (tests/bird.mp3), otherwise some tests will fail.
```
QT_QPA_PLATFORM=offscreen python -m pytest tests -v
```

## Third party licenses
You can use this command to generate third party licenses:
```
pip-licenses --ignore-packages shared --format=plain-vertical --with-license-file --no-license-path --output-file=THIRD_PARTY_LICENSES.txt
```
It can't find all license texts automatically so you have to manually fill in those.

## Changing the app icon

You can use the script resize_icons.sh to create icon sets. The first argument is the path to the source image and the second argument is the path to the output folder.

Create icon set and Windows .ico file
```
./resize_icons.sh sirkku.png icons/logo/iconset
convert icons/logo/iconset/*.png icons/logo/sirkku-logo.ico
```

Remember to compile resources when making changes to icons.
```
pyside6-rcc resources.qrc -o resources.py
```

Update splash screen icon
```
cp sirkku.png icons/logo/sirkku-logo-splash.png
```

MacOS .icns file can be created with Icon Composer and Xcode.
