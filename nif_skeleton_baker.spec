# nif_skeleton_baker.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

# 1) Collect any PyFFI data files if you need them (else, remove this line)
datas = collect_data_files('pyffi')

# 2) Tell PyInstaller where to look for your script (pathex)
#    We set pathex to the folder containing your .py and .ico files.
pathex = [
    r"E:\SkyrimMods\ModdingTools\Prototypoe plugins\nif skeleton baker"
]

block_cipher = None

a = Analysis(
    ['nif_skeleton_baker.py'],
    pathex=pathex,
    binaries=[],
    datas=datas,            # include pyffi data; if you don't need it, set datas=[]
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
    console=False,  # False = windowed (no console)
    icon=r"E:\SkyrimMods\ModdingTools\Prototypoe plugins\nif skeleton baker\my_icon.ico",
)
