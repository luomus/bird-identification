# -*- mode: python ; coding: utf-8 -*-
import pkgutil
import rasterio

# include resampy and all rasterio submodules since they are not detected automatically
additional_packages = ['resampy']
for package in pkgutil.iter_modules(rasterio.__path__, prefix="rasterio."):
    additional_packages.append(package.name)

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../models/Pred_adjustment', 'models/Pred_adjustment'),
        ('../models/classes.csv', 'models'),
        ('../models/BirdNET_GLOBAL_6K_V2.4_Model_FP32.tflite', 'models'),
        ('../models/model_v3_5.h5', 'models')
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
