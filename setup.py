'''Witcher 3 Mod Manager cx_Freeze setup script'''

from cx_Freeze import setup, Executable
import Globals

FILES = ["res/", "translations/", "7-Zip/"]
SHORTCUT_TABLE = [
    (
        "DesktopShortcut",        # Shortcut
        "DesktopFolder",          # Directory_
        Globals.TITLE,            # Name
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
    name=Globals.TITLE,
    version=Globals.VERSION,
    url='https://rd.nexusmods.com/witcher3/mods/2678',
    license='Open-source',
    options={"build_exe": {"include_files":FILES}, "bdist_msi": BDIST_MSI_OPTIONS},
    author='stefan3372',
    author_email='stekos@live.com',
    description=Globals.TITLE,
    executables=[Executable("TheWitcher3ModManager.py", icon='res/w3a.ico', base="Win32GUI")]
)
