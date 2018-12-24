'''Witcher 3 Mod Manager main module'''
# pylint: disable=invalid-name,missing-docstring,bare-except,broad-except

import sys
from ctypes import create_unicode_buffer, wintypes, windll
from os import path, environ
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QTranslator, QCoreApplication

from src.gui.main_window import CustomMainWindow
from src.gui.main_widget import CustomMainWidget
from src.util.util import getIcon, getVersionString, normalizePath
from src.util.syntax import writeAllModsToXMLFile
from src.configuration.config import Configuration
from src.globals import data

TRANSLATE = QCoreApplication.translate


def __getDocuments():
    buf = create_unicode_buffer(wintypes.MAX_PATH)
    windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
    return normalizePath(buf.value)

def __translateToChosenLanguage():
    language = data.config.language
    if (language and path.exists("translations/" + language)):
        translator = QTranslator()
        translator.load("translations/" + language)
        data.app.installTranslator(translator)

if __name__ == "__main__":
    # correct screen scaling without generating warnings
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
    documents = __getDocuments()

    gamePath = ""
    while not data.config:
        try:
            data.config = Configuration(documents, gamePath)
        except Exception as err:
            print(str(err))
            gamePath = str(QFileDialog.getOpenFileName(
                None, "Select witcher3.exe", "witcher3.exe", "*.exe")[0])
            if not gamePath:
                QMessageBox.critical(
                    None,
                    "Selected file not correct",
                    "'witcher3.exe' file not selected",
                    QMessageBox.Ok,
                    QMessageBox.Ok)
                sys.exit()

    __translateToChosenLanguage()

    mainWindow = CustomMainWindow()
    mainWidget = CustomMainWidget(mainWindow)
    mainWindow.dropCallback = mainWidget.InstallModFiles
    data.app.setWindowIcon(getIcon("w3a.ico"))
    mainWindow.show()

    ret = data.app.exec_()
    data.config.saveWindowSettings(mainWidget, mainWindow)
    data.config.write()
    writeAllModsToXMLFile(mainWidget.modList, data.config.configPath + '/installed.xml')

    sys.exit(ret)
