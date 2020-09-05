'''Witcher 3 Mod Manager cx_Freeze setup script'''
# pylint: disable=wildcard-import,unused-wildcard-import

from cx_Freeze import setup, Executable
from src.globals.constants import *

import distutils
import opcode
import os

# opcode is not a virtualenv module, so we can use it to find the stdlib; this is the same
# trick used by distutils itself it installs itself into the virtualenv
distutils_path = os.path.join(os.path.dirname(opcode.__file__), 'distutils')

FILES = ["res/", "translations/", "tools/",
         (distutils_path, 'lib/distutils'), ("res/qt.conf", "qt.conf"), "LICENSE"]
SHORTCUT_TABLE = [
    (
        "DesktopShortcut",        # Shortcut
        "DesktopFolder",          # Directory_
        TITLE,                    # Name
        "TARGETDIR",              # Component_
        "[TARGETDIR]TheWitcher3ModManager.exe",   # Target
        None,                     # Arguments
        None,                     # Description
        None,                     # Hotkey
        None,                     # Icon
        None,                     # IconIndex
        None,                     # ShowCmd
        'TARGETDIR'               # WkDir
    ),
]

MSI_DATA = {"Shortcut": SHORTCUT_TABLE}
BDIST_MSI_OPTIONS = {'data': MSI_DATA}

setup(
    name=TITLE,
    version=VERSION,
    url=URL_WEB,
    license='Open-source',
    options={
        "build_exe": {
            "include_files": FILES,
            "excludes": ["distutils"],
            "optimize": 2,
            "zip_include_packages": ["src"]
        },
        "bdist_msi": BDIST_MSI_OPTIONS},
    author=AUTHORS[1],
    author_email=AUTHORS_MAIL[1],
    description=TITLE,
    executables=[Executable(
        "main.py",
        targetName="TheWitcher3ModManager.exe",
        icon='res/w3a.ico',
        base="Win32GUI"
    )]
)
