'''Witcher 3 Mod Manager main module'''
#pylint: disable=invalid-name

import ctypes
import sys
from os import path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator

from src.gui.gui import CustomMainWindow, CustomMainWidget
from src.util.util import getIcon, saveXML
from src.configuration.config import Configuration
from src.globals import data


def __getDocuments():
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
    return str(buf.value).replace('\\', '/')

def __translateToChosenLanguage():
    language = data.config.language
    if (language and path.exists("translations/" + language)):
        translator = QTranslator()
        translator.load("translations/" + language)
        data.app.installTranslator(translator)

if __name__ == "__main__":
    documents = __getDocuments()
    data.config = Configuration(documents)
    data.app = QApplication(sys.argv)
    __translateToChosenLanguage()

    mainWindow = CustomMainWindow()
    mainWidget = CustomMainWidget(None, mainWindow)
    mainWindow.dropCallback = mainWidget.InstallModFiles
    data.app.setWindowIcon(getIcon("w3a.ico"))
    mainWindow.show()

    ret = data.app.exec_()
    data.config.saveWindowSettings(mainWidget, mainWindow)
    data.config.write()
    saveXML(mainWidget.modList)

    sys.exit(ret)

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)

#     initconfig()
#     language = getini('SETTINGS', 'language')
#     if (language and path.exists("translations/" + language)):
#         translator = QtCore.QTranslator()
#         translator.load("translations/" + language)
#         app.installTranslator(translator)

#     ui = Ui_MainWindow()
#     MainWindow = CustomMainWindow(ui)
#     ui.setupUi(MainWindow)
#     app.setWindowIcon(getIcon("w3a.ico"))
#     MainWindow.show()

#     ret = app.exec_()
#     savewindowsettings(ui, MainWindow)
#     iniwrite()
#     saveXML(ui.modList)

#     sys.exit(ret)
