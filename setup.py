'''Witcher 3 Mod Manager cx_Freeze setup script'''
# pylint: disable=wildcard-import,unused-wildcard-import

from cx_Freeze import setup, Executable
from src.globals.constants import *

FILES = ["res/", "translations/", "7-Zip/"]
SHORTCUT_TABLE = [
    (
        "DesktopShortcut",        # Shortcut
        "DesktopFolder",          # Directory_
        TITLE,            # Name
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
    options={"build_exe": {"include_files":FILES}, "bdist_msi": BDIST_MSI_OPTIONS},
    author=AUTHORS[0],
    author_email=AUTHORS_MAIL[0],
    description=TITLE,
    executables=[Executable("TheWitcher3ModManager.py", icon='res/w3a.ico', base="Win32GUI")]
)
