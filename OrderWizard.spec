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

# 定义要包含的数据文件
additional_datas = [
    ('static', 'static'),
]

# 仅当icon.icns存在时才添加
if os.path.exists('icon.icns'):
    additional_datas.append(('icon.icns', '.'))
else:
    print("Warning: icon.icns not found. The application will be built without an icon.")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=tkdnd_files,
    datas=additional_datas,
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
    icon=['icon.icns'] if os.path.exists('icon.icns') else None,
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
    icon='icon.icns' if os.path.exists('icon.icns') else None,
    bundle_identifier=None,
)
