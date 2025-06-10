# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('pyffi')

block_cipher = None

a = Analysis(
    ['nif_skeleton_baker.py'],
    pathex=[r"E:\SkyrimMods\ModdingTools\Prototypoe plugins\nif skeleton baker"],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='nif_skeleton_baker',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
