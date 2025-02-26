# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path
from site import getsitepackages

block_cipher = None

# Find tkdnd library path
site_packages = getsitepackages()
tkdnd_path = None
for site_package in site_packages:
    possible_path = os.path.join(site_package, 'tkinterdnd2', 'tkdnd')
    if os.path.exists(possible_path):
        tkdnd_path = possible_path
        break

if not tkdnd_path:
    raise Exception("Could not find tkdnd library")

# Add TCL/TK files
from PyInstaller.utils.hooks import collect_data_files
tcl_tk_data = collect_data_files('tkinterdnd2', include_py_files=True)

# Find tcl/tk libraries
import tkinter
tcl_root = os.path.dirname(os.path.dirname(tkinter.__file__))
tcl_lib = os.path.join(tcl_root, 'lib', 'tcl8.6')
tk_lib = os.path.join(tcl_root, 'lib', 'tk8.6')

# Add tcl/tk libraries to datas
tcl_tk_files = []
if os.path.exists(tcl_lib):
    tcl_tk_files.extend([
        (tcl_lib, 'lib/tcl8.6'),
        (tk_lib, 'lib/tk8.6')
    ])

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images', 'images'),  # Include images directory
        ('orders.db', '.'),    # Include database file if it exists
        ('ui', 'ui'),         # Include UI module
        ('db', 'db'),         # Include database module
        ('model', 'model'),   # Include model module
        (tkdnd_path, 'tkinterdnd2/tkdnd'),  # Include tkdnd library
    ] + tcl_tk_data + tcl_tk_files,  # Add TCL/TK files here
    hiddenimports=[
        'tkinter',
        'tkinterdnd2',
        'ttkbootstrap',
        'PIL',
        'PIL._tkinter_finder',
        'PIL.Image',
        'sqlite3',
        'logging',
        '_tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.dnd'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OrderWizard',
)

app = BUNDLE(
    coll,
    name='OrderWizard.app',
    icon=None,
    bundle_identifier='com.orderwizard.app',
    info_plist={
        'CFBundleName': 'OrderWizard',
        'CFBundleDisplayName': 'OrderWizard',
        'CFBundleExecutable': 'OrderWizard',
        'CFBundlePackageType': 'APPL',
        'CFBundleSupportedPlatforms': ['MacOSX'],
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSEnvironment': {
            'ORDERWIZARD_DEBUG': '1',
            'PYTHONUNBUFFERED': '1',
            'TKDND_LIBRARY': '@executable_path/../Resources/tkinterdnd2/tkdnd',
            'TCL_LIBRARY': '@executable_path/../Resources/lib/tcl8.6',
            'TK_LIBRARY': '@executable_path/../Resources/lib/tk8.6'
        },
        'LSBackgroundOnly': False,
        'NSAppleEventsUsageDescription': 'OrderWizard needs to handle system events.',
        'CFBundleDocumentTypes': [],
        'CFBundleTypeRole': 'Viewer',
        'LSApplicationCategoryType': 'public.app-category.business',
    }
) 