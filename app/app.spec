# -*- mode: python ; coding: utf-8 -*-

datas = [
    ('./models', 'models'),
    ('LICENSE.txt', '.'),
    ('THIRD_PARTY_LICENSES.txt', '.'),
]

main_a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
main_pyz = PYZ(main_a.pure)
main_exe = EXE(
    main_pyz,
    main_a.scripts,
    [],
    exclude_binaries=True,
    name='sirkku',
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
    version='version_info.txt',
    icon='icons/logo/sirkku-logo.ico'
)

analyze_a = Analysis(
    ['analyze_process.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['resampy'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
analyze_pyz = PYZ(analyze_a.pure)
analyze_exe = EXE(
    analyze_pyz,
    analyze_a.scripts,
    [],
    exclude_binaries=True,
    name='sirkkuAnalyze',
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
    version='version_info_analyze.txt'
)

coll = COLLECT(
    main_exe,
    main_a.binaries,
    main_a.datas,
    analyze_exe,
    analyze_a.binaries,
    analyze_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='sirkku',
)

app = BUNDLE(
    coll,
    name='Sirkku.app',
    icon='icons/logo/sirkku-logo.icns',
    bundle_identifier='fi.laji.sirkku',
    version='{{ version }}',
    info_plist={
        'CFBundleName': 'Sirkku',
        'NSHumanReadableCopyright': '© 2025 Luomus - Finnish Museum of Natural History'
    }    
)
