# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\AbogadoVirtual\\04_Aplicaciones_UI\\lanzador_inmobiliario.py'],
    pathex=[],
    binaries=[],
    datas=[('chroma_db', 'chroma_db'), ('ollama_bin', 'ollama_bin'), ('normativa_pdf', 'normativa_pdf')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='Guanes_Inmobiliario_V5',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icon.ico'],
)
