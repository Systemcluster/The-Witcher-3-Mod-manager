'''Witcher 3 Mod Manager cx_Freeze setup script'''
# pylint: disable=wildcard-import,unused-wildcard-import

from cx_Freeze import Executable, setup

from src.globals.constants import *

FILES = ["res/", "translations/", "tools/",
         ("res/qt.conf", "qt.conf"), "LICENSE"]
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
            "excludes": ["distutils", "patool"],
            "optimize": 2,
            "zip_include_packages": ["src"],
            "include_msvcr": True
        },
        "bdist_msi": BDIST_MSI_OPTIONS},
    author=AUTHORS[1],
    author_email=AUTHORS_MAIL[1],
    description=TITLE,
    executables=[Executable(
        "main.py",
        target_name="TheWitcher3ModManager.exe",
        icon='res/w3a.ico',
        base="Win32GUI"
    )]
)
