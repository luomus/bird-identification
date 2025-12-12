# -*- mode: python ; coding: utf-8 -*-


main_a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('./models', 'models'),
    ],
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
    version='version_info.txt'
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
    name='birdIdentifierAnalyze',
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
    name='birdIdentifier',
)

app = BUNDLE(
    coll,
    name='birdIdentifier.app',
    icon=None,
    bundle_identifier='fi.laji.birdIdentifier',
    version='{{ version }}',
    info_plist={
        'CFBundleName': 'Bird Identifier',
        'NSHumanReadableCopyright': '© 2025 Luomus - Finnish Museum of Natural History'
    }    
)
