'''Witcher 3 Mod Manager main module'''
# pylint: disable=invalid-name,missing-docstring,bare-except,broad-except,wildcard-import,unused-wildcard-import

import sys
from argparse import ArgumentParser
from os import environ

if __name__ == "__main__":
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        from src.configuration.config import Configuration
        from src.core.model import Model
        from src.globals import data
        from src.gui.alerts import *
        from src.gui.main_widget import CustomMainWidget
        from src.gui.main_window import CustomMainWindow
        from src.util.util import *

        # correct screen scaling
        if "QT_DEVICE_PIXEL_RATIO" in environ:
            del environ["QT_DEVICE_PIXEL_RATIO"]
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        documentsPath: str = ''
        gamePath: str = ''
        configPath: str = ''
        try:
            parser = ArgumentParser(description=getVersionString())
            parser.add_argument(
                "-d", "--debug", dest="debug", action="store_true", default=False,
                help="show debug information on errors")
            parser.add_argument(
                "-v", "--version", dest="version", action="store_true", default=False,
                help="show version information and exit")
            dirs = parser.add_argument_group(
                title='start overrides'
            )
            dirs.add_argument(
                "-u", "--userdocuments", dest="userdocuments", type=str, default="",
                help="override the documents path")
            dirs.add_argument(
                "-g", "--game", dest="game", type=str, default="",
                help="override the game path")
            dirs.add_argument(
                "-c", "--config", dest="config", type=str, default="",
                help="override the config path")
            args = parser.parse_args()
            data.debug = args.debug
            if args.version:
                print(getVersionString())
                sys.exit()
            documentsPath = args.userdocuments
            gamePath = args.game
            configPath = args.config
        except Exception as e:
            print(str(e))

        data.app = QApplication(sys.argv)
        data.config = Configuration(documentsPath, gamePath, configPath)
        translateToChosenLanguage()

        if not Configuration.getCorrectGamePath(data.config.gameexe):
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

        ret = data.app.exec()
        data.config.saveWindowSettings(mainWidget, mainWindow)
        data.config.write_priority().join()
        data.config.write_config().join()
        modModel.write()

        sys.exit(ret)

    except Exception as e:
        import traceback

        from src.util.util import formatUserError
        print(formatUserError(e), file=sys.stderr)
        try:
            if sys.platform == "win32":
                import win32api  # pylint: disable=import-error # type: ignore
                win32api.MessageBox(
                    0, f'{str(e)}\n\n{traceback.format_exc()}', "Unexpected Error", 0x10)
        except Exception as x:
            print("Failed to show error message: " +
                  formatUserError(x), file=sys.stderr)
        sys.exit(1)
