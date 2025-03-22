# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

tkdnd_path = '/Users/spenc/miniconda3/envs/OrderWizard/lib/python3.12/site-packages/tkinterdnd2/tkdnd/osx-arm64'

# Collect all tkdnd files
tkdnd_files = [
    (os.path.join(tkdnd_path, 'libtkdnd2.9.3.dylib'), '.'),
    (os.path.join(tkdnd_path, 'pkgIndex.tcl'), '.'),
    (os.path.join(tkdnd_path, 'tkdnd.tcl'), '.'),
    (os.path.join(tkdnd_path, 'tkdnd_macosx.tcl'), '.'),
    (os.path.join(tkdnd_path, 'tkdnd_unix.tcl'), '.'),
    (os.path.join(tkdnd_path, 'tkdnd_utils.tcl'), '.'),
    (os.path.join(tkdnd_path, 'tkdnd_generic.tcl'), '.'),
    (os.path.join(tkdnd_path, 'tkdnd_compat.tcl'), '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=tkdnd_files,
    datas=[('dmg_staging/Applications/OrderWizard.app/Contents/Resources', 'Resources')],
    hiddenimports=['tkinterdnd2'],
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
    name='OrderWizard',
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
    icon=['icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrderWizard',
)
app = BUNDLE(
    coll,
    name='OrderWizard.app',
    icon='icon.icns',
    bundle_identifier=None,
)
