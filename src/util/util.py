'''Global Helpers'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring,wildcard-import,unused-wildcard-import

import os
import sys
import re
import traceback
import webbrowser
import subprocess
from shutil import copytree
from distutils import dir_util
from platform import python_version
from ctypes import create_unicode_buffer, wintypes, windll

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from src.globals import data
from src.globals.constants import *
from src.gui.file_dialog import FileDialog


def formatUserError(error: str) -> str:
    print(traceback.format_exc(), error, file=sys.stderr)
    if data.debug:
        return traceback.format_exc() + str(error)
    else:
        return str(error)

def getDocumentsFolder() -> str:
    buf = create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
    return normalizePath(buf.value)

def getVersionString() -> str:
    return TITLE + " " + VERSION

def normalizePath(path: str) -> str:
    return os.path.normpath(str(path)).replace('\\', '/')

def reconfigureGamePath() -> bool:
    gamePath = str(QFileDialog.getOpenFileName(
        None,
        TRANSLATE("MainWindow", "Select witcher3.exe"),
        data.config.gameexe or "witcher3.exe",
        "*.exe")[0])
    try:
        data.config.game = gamePath
    except ValueError as err:
        print(str(err), file=sys.stderr)
        QMessageBox.critical(
            None,
            TRANSLATE("MainWindow", "Selected file not correct"),
            TRANSLATE("MainWindow", "'witcher3.exe' file not selected"),
            QMessageBox.Ok,
            QMessageBox.Ok)
        return False
    return True

def reconfigureScriptMergerPath() -> bool:
    mergerPath = str(QFileDialog.getOpenFileName(
        None,
        TRANSLATE("MainWindow", "Select script merger .exe"),
        data.config.scriptmerger or '',
        "*.exe")[0])
    if mergerPath:
        data.config.scriptmerger = mergerPath

def showAboutWindow():
    QMessageBox.about(
        None,
        TRANSLATE("MainWindow", "About"),
        TRANSLATE(
            "MainWindow",
            ""+TITLE+"\n"
            "Version: "+VERSION+"\n"
            "Authors: "+(", ".join(AUTHORS))+"\n"
            "\n"
            "Written in: Python "+python_version()+"\n"
            "GUI: PyQt "+QtCore.PYQT_VERSION_STR+"\n"
            "\n"
            "Thank you for using "+TITLE+"!"))

def openUrl(url: str):
    webbrowser.open(url)

def openFile(path: str):
    if isExecutable(path):
        directory, _ = os.path.split(path)
        subprocess.Popen([path], cwd=directory)
    else:
        openFolder(path)

def openFolder(path: str):
    while path and not os.path.isdir(path):
        path, _ = os.path.split(path)
    os.startfile(path, "explore")

def copyFolder(src, dst):
    '''Copy folder from src to dst'''
    if (not os.path.exists(dst)):
        copytree(src, dst)
    else:
        dir_util.copy_tree(src, dst)

def restartProgram():
    '''Restarts the program'''
    data.config.write()
    python = sys.executable
    os.execl(python, python, *sys.argv)

def getFile(directory="", extensions="", title="Select Files or Folders"):
    '''Opens custom dialog for selecting multiple folders or files'''
    return FileDialog(None, title, str(directory), str(extensions)).selectedFiles

def getSize(start_path='.'):
    '''Calculates the size of the selected folder'''
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def getIcon(filename):
    '''Gets icon from the res folder'''
    icon = QtGui.QIcon()
    icon.addFile('res/' + filename)
    return icon

def getKey(item):
    '''Helper function for the mod list'''
    return item[1]

def isData(name):
    '''Checks if given name represents correct mod folder or not'''
    return re.match(r"^(~|)mod.+$", name)

def isExecutable(name: str) -> bool:
    _, ext = os.path.splitext(name)
    return ext in ('.exe', '.bat')

def translateToChosenLanguage() -> bool:
    language = data.config.language
    if (language and os.path.exists("translations/" + language)):
        print("loading translation", language)
        data.translator.load("translations/" + language)
        if not data.app.installTranslator(data.translator):
            print("loading translation failed", file=sys.stderr)
            return False
        return True
    else:
        print("chosen language not found:", language, file=sys.stderr)
        return False
