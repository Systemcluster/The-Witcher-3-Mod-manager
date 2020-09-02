'''Witcher 3 Mod Manager main module'''
# pylint: disable=invalid-name,missing-docstring,bare-except,broad-except,wildcard-import,unused-wildcard-import

import sys
import os
import re
from os import environ
from argparse import ArgumentParser

from PySide2.QtWidgets import QApplication, QMessageBox

from src.gui.main_window import CustomMainWindow
from src.gui.main_widget import CustomMainWidget
from src.gui.alerts import *
from src.util.util import *
from src.configuration.config import Configuration
from src.core.model import Model
from src.globals import data
from src.globals.constants import TRANSLATE


if __name__ == "__main__":
    # correct screen scaling
    if "QT_DEVICE_PIXEL_RATIO" in environ:
        del environ["QT_DEVICE_PIXEL_RATIO"]
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    try:
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
    except Exception as e:
        print(str(e))

    data.app = QApplication(sys.argv)
    data.config = Configuration()
    translateToChosenLanguage()

    if not Configuration.getCorrectGamePath(data.config.game):
        if not reconfigureGamePath():
            sys.exit(1)

    try:
        modModel = Model()
    except IOError as err:
        print(err, file=sys.stderr)
        if MessageAlertOtherInstance() == QMessageBox.Yes:
            modModel = Model(ignorelock=True)
        else:
            sys.exit(1)
    except Exception as e:
        MessageInitializationFailed(formatUserError(e))
        sys.exit(1)

    fixUserSettingsDuplicateBrackets()

    mainWindow = CustomMainWindow()
    mainWidget = CustomMainWidget(mainWindow, modModel)
    mainWindow.dropCallback = mainWidget.installModFiles
    data.app.setWindowIcon(getIcon("w3a.ico"))

    mainWindow.show()

    ret = data.app.exec_()
    data.config.saveWindowSettings(mainWidget, mainWindow)
    data.config.write()
    modModel.write()

    sys.exit(ret)
