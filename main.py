'''Witcher 3 Mod Manager main module'''
# pylint: disable=invalid-name,missing-docstring,bare-except,broad-except,wildcard-import,unused-wildcard-import

import sys
from ctypes import create_unicode_buffer, wintypes, windll
from os import path, environ
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator

from src.gui.main_window import CustomMainWindow
from src.gui.main_widget import CustomMainWidget
from src.util.util import *
from src.util.syntax import writeAllModsToXMLFile
from src.configuration.config import Configuration
from src.globals import data
from src.globals.constants import TRANSLATE


def __getDocuments():
    buf = create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
    return normalizePath(buf.value)

translator: QTranslator = QTranslator()
def __translateToChosenLanguage():
    language = data.config.language
    if (language and path.exists("translations/" + language)):
        print("loading translation", language)
        translator.load("translations/" + language)
        if not data.app.installTranslator(translator):
            print("loading translation failed", file=sys.stderr)
    else:
        print("chosen language not found:", language, file=sys.stderr)

if __name__ == "__main__":
    # correct screen scaling
    if "QT_DEVICE_PIXEL_RATIO" in environ:
        del environ["QT_DEVICE_PIXEL_RATIO"]
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    parser = ArgumentParser(description=getVersionString())
    parser.add_argument(
        "-d", "--debug", dest="debug", action="store_true", default=False,
        help="show debug information on errors")
    parser.add_argument(
        "-v", "--version", dest="version", action="store_true", default=False,
        help="show version information and exit")
    args = parser.parse_args()
    data.debug = args.debug
    if args.version:
        print(getVersionString())
        sys.exit()

    data.app = QApplication(sys.argv)
    data.config = Configuration(__getDocuments())

    __translateToChosenLanguage()

    if not Configuration.getCorrectGamePath(data.config.game):
        if not reconfigureGamePath():
            sys.exit()

    mainWindow = CustomMainWindow()
    mainWidget = CustomMainWidget(mainWindow)
    mainWindow.dropCallback = mainWidget.installModFiles
    data.app.setWindowIcon(getIcon("w3a.ico"))
    mainWindow.show()

    ret = data.app.exec_()
    data.config.saveWindowSettings(mainWidget, mainWindow)
    data.config.write()
    writeAllModsToXMLFile(mainWidget.model.all(), data.config.configuration + '/installed.xml')

    sys.exit(ret)
