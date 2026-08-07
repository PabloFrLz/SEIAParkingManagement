# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = [('imagens', 'imagens')]
datas += collect_data_files('paddlex')
datas += collect_data_files('paddleocr')
datas += copy_metadata('paddlex')
datas += copy_metadata('paddleocr')
datas += copy_metadata('paddlepaddle')
datas += copy_metadata('pyclipper')
datas += copy_metadata('shapely')
datas += copy_metadata('imagesize')
datas += copy_metadata('opencv-contrib-python')
datas += copy_metadata('pypdfium2')
datas += copy_metadata('python-bidi')
datas += copy_metadata('safetensors')


a = Analysis(
    ['SEIAParkingManagement.py'],
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
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SEIAParkingManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=['icone.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SEIAParkingManagement',
)
