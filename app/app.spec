# -*- mode: python ; coding: utf-8 -*-

# include resampy since it's not detected automatically
additional_packages = ['resampy']

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../models/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite', 'data'),
        ('../models/Pred_adjustment/calibration_params.npy', 'models/Finnish_model_v3_5'),
        ('../models/classes.csv', 'models/Finnish_model_v3_5'),
        ('../models/model_v3_5.h5', 'models/Finnish_model_v3_5'),
        ('./build_resources/metadata.json', 'models/Finnish_model_v3_5')
    ],
    hiddenimports=additional_packages,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='birdIdentifier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='birdIdentifier',
)
