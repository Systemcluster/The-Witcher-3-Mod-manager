from cx_Freeze import setup, Executable
files =["res/", "translations/", "7-Zip/"]
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "The Witcher 3 Mod Manager",     # Name
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

msi_data = {"Shortcut": shortcut_table}
bdist_msi_options = {'data': msi_data}

setup(
    name='The Witcher 3 Mod Manager',
    version='0.6.2',
    url='https://rd.nexusmods.com/witcher3/mods/2678',
    license='Open-source',
    options={"build_exe": {"include_files":files}, "bdist_msi": bdist_msi_options},
    author='stefan3372',
    author_email='stekos@live.com',
    description='The Witcher 3 Mod Manager',
    executables=[Executable("TheWitcher3ModManager.py", icon='res/w3a.ico', base = "Win32GUI")]
)
