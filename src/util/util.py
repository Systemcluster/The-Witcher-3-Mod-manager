'''Global Helpers'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring,wildcard-import,unused-wildcard-import

import os
import sys
import re
from shutil import copytree
from distutils import dir_util
import traceback

from PyQt5 import QtGui

from src.globals import data
from src.globals.constants import *
from src.gui.file_dialog import FileDialog

def formatUserError(error: str) -> str:
    print(traceback.format_exc(), error, file=sys.stderr)
    if data.debug:
        return traceback.format_exc() + str(error)
    else:
        return str(error)

def getVersionString() -> str:
    return TITLE + " " + VERSION

def normalizePath(path: str) -> str:
    return os.path.normpath(str(path)).replace('\\', '/')

def restart_program():
    '''Restarts the program'''
    data.config.write()
    python = sys.executable
    os.execl(python, python, *sys.argv)

def copyfolder(src, dst):
    '''Copy folder from src to dst'''
    if (not os.path.exists(dst)):
        copytree(src, dst)
    else:
        dir_util.copy_tree(src, dst)


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
