'''Alert Dialogs'''
# pylint: disable=invalid-name,wildcard-import,unused-wildcard-import

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from src.globals.constants import *


def MessageRebindKeys(current, modded, category, justModifiers=False):
    '''Shows dialog to let user decide what to do if key rebind with same action but different modifiers is found'''
    if justModifiers:
        additional = translate("MainWindow", "The new keybind for the same action has different modifiers than the current keybind.") + "\n\n" + \
            translate("MainWindow", "Replace modifiers?")
    else:
        additional = translate("MainWindow", "The new keybind changes the key for an existing action.") + "\n\n" + \
            translate("MainWindow", "Replace keybind and modifiers?")
    return QMessageBox.question(
        None,
        translate("MainWindow", "Key Rebind Found"),
        translate("MainWindow", "Key rebind found.") + "\n\n" +
        translate("MainWindow", "Category: ") + "\n  " + category + "\n\n" +
        translate("MainWindow", "Current keybind: ") + "\n  " + str(current) + "\n" +
        translate("MainWindow", "New mod keybind: ") + "\n  " + str(modded) + "\n\n" +
        additional,
        QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.No | QMessageBox.NoToAll,
        QMessageBox.Yes)


def MessageOverwrite(modname, modtype):
    '''Shows dialog to let user decide what to do if mod is already installed'''
    return QMessageBox.question(
        None,
        translate("MainWindow", "Mod already installed"),
        str(modtype) + " '" + str(modname) + "' " + translate(
            "MainWindow",
            "is already installed.") + "\n" + translate("MainWindow", "Do you want to overwrite the existing files?"),
        QMessageBox.Yes | QMessageBox.YesToAll |
        QMessageBox.No | QMessageBox.NoToAll,
        QMessageBox.Yes)


def MessageAlertScript():
    '''Shows dialog to let user know he/she should run script merger \
        after each change in the mod list'''
    return QMessageBox.question(
        None,
        translate("MainWindow", "Run Script Merger"),
        translate(
            "MainWindow",
            "After changing the mod list in any way you should run script merger to merge "
            "the mods and ensure their compatibility and remove previously merged scripts") +
        translate(
            "MainWindow",
            "Do you want to run it now?")+"\n\n" +
        translate(
            "MainWindow",
            "Note: You can disable these alerts in the settings..."),
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


def MessageAlertIncompleteInstallation():
    '''Shows dialog to let user know that the installation is incomplete'''
    return QMessageBox.information(
        None,
        translate("MainWindow", "Incomplete Installation"),
        translate(
            "MainWindow",
            "The installation of a mod is incomplete.") + "\n\n" +
        translate(
            "MainWindow",
            "Some files might have to be installed manually.") + "\n" +
        translate(
            "MainWindow",
            "Please check the output log for more information.") + "\n",
        QMessageBox.Ok
    )


def MessageAlertOtherInstance():
    '''Shows alert that another insntance is already open'''
    return QMessageBox.question(
        None,
        translate("MainWindow", "Already Running"),
        translate(
            "MainWindow",
            "Another instance of ")+TITLE +
        translate(
            "MainWindow",
            " is already running.")+"\n" +
        translate(
            "MainWindow",
            "Opening more than one instance can result in an invalid configuration.")+"\n\n" +
        translate(
            "MainWindow",
            "Do you want to continue anyway?"),
        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)


def MessageInitializationFailed(error: str):
    '''Shows alert that application initialization failed'''
    message = QMessageBox(None)
    message.setWindowTitle(translate("MainWindow", "Startup Error"))
    message.setText(translate(
        "MainWindow",
        "<b>Initialization of the mod list failed.</b><br><br>"
        "It is possible that you have an error in your configuration file <code>installed.xml</code>.<br>"
        "Detailed error below."))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{error}")
    return message.exec()


def MessageCouldntOpenFile(file: str, error: str):
    '''Shows alert that a file couldn't be opened'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(translate("MainWindow", "Couldn't Open File"))
    message.setText(
        translate("MainWindow", "Couln't open the file:<br>") +
        f"<code>{file}</code><br><br>" +
        translate("MainWindow", "Does it exist?"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{error}")
    return message.exec()


def MessageUnsupportedOS(os: str):
    '''Shows alert that the OS is not supported'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(translate("MainWindow", "Unsupported OS"))
    message.setText(
        translate("MainWindow", "Unsupported OS:<br>") +
        f"<code>{os}</code><br><br>")
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec()


def MessageUnsupportedOSAction(message: str):
    '''Shows alert that an action is not supported on the OS'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(
        translate("MainWindow", "Action not supported on this OS"))
    message.setText(
        translate("MainWindow", "Action not supported on this OS.<br>") +
        f"{message}<br><br>")
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec()


def MessageAlertWritingFailed(path: str, error: Exception):
    '''Shows alert that writing to a file failed'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(translate("MainWindow", "Failed to write file"))
    message.setText(
        translate("MainWindow", "Failed to write to a file:<br>") +
        f"<code>{path}</code><br><br>" +
        translate("MainWindow", "Please check if the file is still valid.<br>" +
                  "Otherwise check if a .old copy exists in its location and copy over its contents.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec()


def MessageAlertReadingConfigurationFailed(path: str, error: Exception):
    '''Shows alert that reading a configuration file failed'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(
        translate("MainWindow", "Failed to read configuration file"))
    message.setText(
        translate("MainWindow", "Failed to read a configuration file:<br>") +
        f"<code>{path}</code><br><br>" +
        translate("MainWindow", "Please check if the file is still valid.<br>"
                  "Otherwise check if a .old copy exists in its location and copy over its contents.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec()


def MessageAlertReadingConfigINI(path: str, error: Exception):
    '''Shows alert that reading the config.ini file failed'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(
        translate("MainWindow", "Failed to read configuration file"))
    message.setText(
        translate("MainWindow", "Failed to read the configuration file:<br>") +
        f"<code>{path}</code><br><br>" +
        translate("MainWindow", "The program will start with a new configuration.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec()


def MessageNotConfigured():
    '''Shows alert that the game path configuration is missing'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Information)
    message.setWindowTitle(
        translate("MainWindow", "The Witcher 3 Mod Manager - Configuration"))
    message.setText(
        translate("MainWindow", "Welcome! Please select your <code>witcher3.exe</code> in the next dialog.<br><br>"
                  "This file can be found in the games installation directory under <code>bin/x64/witcher3.exe</code> or <code>bin/x64_dx12/witcher3.exe</code>.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec()


def MessageNotConfiguredScriptMerger():
    '''Shows alert that the script merger path configuration is missing'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Information)
    message.setWindowTitle(
        translate("MainWindow", "The Witcher 3 Mod Manager - Configuration"))
    message.setText(
        translate("MainWindow", "Please select your <code>WitcherScriptMerger.exe</code> in the next dialog.<br><br>" +
                  "Script Merger is not included and has to be downloaded separately.<br>" +
                  "It can be found at <a href=\"https://www.nexusmods.com/witcher3/mods/484\">https://www.nexusmods.com/witcher3/mods/484</a><br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec()


def MessageAlertModFromGamePath(modPath, gamePath):
    '''Shows alert that adding mods from the game's directory is not supported'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Information)
    message.setWindowTitle(
        translate("MainWindow", "Invalid Mod Location"))
    message.setText(
        translate("MainWindow", "Adding mods from within the game's directory is not supported.<br>" +
                  "If you want to add existing mods to the manager you have to uninstall them first.<br><br>") +
        translate("MainWindow", "Mod locaion: ") + modPath + "<br>" +
        translate("MainWindow", "Game location: ") + gamePath + "<br><br>")
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec()


def MessageAlertCriticalError(error: Exception):
    '''Shows alert that a critical error occured'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Critical)
    message.setWindowTitle(translate("MainWindow", "Unexpected Error"))
    message.setText(
        translate("MainWindow", "An unexpected error occured.<br>") +
        translate("MainWindow", "See the detailed error below.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec()
