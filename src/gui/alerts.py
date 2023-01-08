'''Alert Dialogs'''
# pylint: disable=invalid-name,wildcard-import,unused-wildcard-import

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMessageBox

from src.globals.constants import *


def MessageRebindedKeys(key, temp):
    '''Shows dialog to let user decide what to do if rebinded key is found'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Key Rebinding Found"),
        TRANSLATE("MainWindow", "Key rebinding found.") + "\n\n" +
        TRANSLATE("MainWindow", "New key: ") + "\n  " + str(key) + "\n" +
        TRANSLATE("MainWindow", "Current key: ") + "\n  " + str(temp) + "\n\n" +
        TRANSLATE("MainWindow", "Do you wish to keep your current key?"),
        QMessageBox.Yes | QMessageBox.YesToAll |
        QMessageBox.No | QMessageBox.NoToAll | QMessageBox.SaveAll,
        QMessageBox.Yes)


def MessageOverwrite(modname, modtype):
    '''Shows dialog to let user decide what to do if mod is already installed'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Mod already installed"),
        str(modtype) + " '" + str(modname) + "' " + TRANSLATE(
            "MainWindow",
            "is already installed.") + "\n" + TRANSLATE("MainWindow", "Do you want to overwrite the existing files?"),
        QMessageBox.Yes | QMessageBox.YesToAll |
        QMessageBox.No | QMessageBox.NoToAll,
        QMessageBox.Yes)


def MessageAlertScript():
    '''Shows dialog to let user know he/she should run script merger \
        after each change in the mod list'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Run Script Merger"),
        TRANSLATE(
            "MainWindow",
            "After changing the mod list in any way you should run script merger to merge "
            "the mods and ensure their compatibility and remove previously merged scripts")+
        TRANSLATE(
            "MainWindow",
            "Do you want to run it now?")+"\n"+
            "\n"+
        TRANSLATE(
            "MainWindow",
            "Note: You can disable these alerts in the settings..."),
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)


def MessageAlertOtherInstance():
    '''Shows alert that another insntance is already open'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Already Running"),
        TRANSLATE(
            "MainWindow",
            "Another instance of ")+TITLE+
        TRANSLATE(
            "MainWindow",
            " is already running.")+"\n"+
        TRANSLATE(
            "MainWindow",
            "Opening more than one instance can result in an invalid configuration.")+"\n"+
            "\n"+
        TRANSLATE(
            "MainWindow",
            "Do you want to continue anyway?"),
        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)


def MessageInitializationFailed(error: str):
    '''Shows alert that application initialization failed'''
    message = QMessageBox(None)
    message.setWindowTitle(TRANSLATE("MainWindow", "Startup Error"))
    message.setText(TRANSLATE(
        "MainWindow",
        "<b>Initialization of the mod list failed.</b><br><br>"
        "It is possible that you have an error in your configuration file <code>installed.xml</code>.<br>"
        "Detailed error below."))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{error}")
    return message.exec_()


def MessageCouldntOpenFile(file: str, error: str):
    '''Shows alert that a file couldn't be opened'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(TRANSLATE("MainWindow", "Couldn't Open File"))
    message.setText(
        TRANSLATE("MainWindow", "Couln't open the file:<br>") +
        f"<code>{file}</code><br><br>" +
        TRANSLATE("MainWindow", "Does it exist?"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{error}")
    return message.exec_()


def MessageUnsupportedOS(os: str):
    '''Shows alert that the OS is not supported'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(TRANSLATE("MainWindow", "Unsupported OS"))
    message.setText(
        TRANSLATE("MainWindow", "Unsupported OS:<br>") +
        f"<code>{os}</code><br><br>")
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec_()


def MessageUnsupportedOSAction(message: str):
    '''Shows alert that an action is not supported on the OS'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(
        TRANSLATE("MainWindow", "Action not supported on this OS"))
    message.setText(
        TRANSLATE("MainWindow", "Action not supported on this OS.<br>") +
        f"{message}<br><br>")
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec_()


def MessageAlertWritingFailed(path: str, error: Exception):
    '''Shows alert that writing to a file failed'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(TRANSLATE("MainWindow", "Failed to write file"))
    message.setText(
        TRANSLATE("MainWindow", "Failed to write to a file:<br>") +
        f"<code>{path}</code><br><br>" +
        TRANSLATE("MainWindow", "Please check if the file is still valid.<br>" +
        "Otherwise check if a .old copy exists in its location and copy over its contents.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec_()


def MessageAlertReadingConfigurationFailed(path: str, error: Exception):
    '''Shows alert that reading a configuration file failed'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(
        TRANSLATE("MainWindow", "Failed to read configuration file"))
    message.setText(
        TRANSLATE("MainWindow", "Failed to read a configuration file:<br>") +
        f"<code>{path}</code><br><br>" +
        TRANSLATE("MainWindow", "Please check if the file is still valid.<br>"
        "Otherwise check if a .old copy exists in its location and copy over its contents.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec_()


def MessageAlertReadingConfigINI(path: str, error: Exception):
    '''Shows alert that reading the config.ini file failed'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Warning)
    message.setWindowTitle(
        TRANSLATE("MainWindow", "Failed to read configuration file"))
    message.setText(
        TRANSLATE("MainWindow", "Failed to read the configuration file:<br>") +
        f"<code>{path}</code><br><br>" +
        TRANSLATE("MainWindow", "The program will start with a new configuration.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    message.setDetailedText(f"{str(error)}")
    return message.exec_()


def MessageNotConfigured():
    '''Shows alert that the game path configuration is missing'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Information)
    message.setWindowTitle(
        TRANSLATE("MainWindow", "The Witcher 3 Mod Manager - Configuration"))
    message.setText(
        TRANSLATE("MainWindow", "Welcome! Please select your <code>witcher3.exe</code> in the next dialog.<br><br>"
        "This file can be found in the games installation directory under <code>bin/x64/witcher3.exe</code> or <code>bin/x64_dx12/witcher3.exe</code>.<br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec_()


def MessageNotConfiguredScriptMerger():
    '''Shows alert that the script merger path configuration is missing'''
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Information)
    message.setWindowTitle(
        TRANSLATE("MainWindow", "The Witcher 3 Mod Manager - Configuration"))
    message.setText(
        TRANSLATE("MainWindow", "Please select your <code>WitcherScriptMerger.exe</code> in the next dialog.<br><br>" +
        "Script Merger is not included and has to be downloaded separately.<br>" +
        "It can be found at <a href=\"https://www.nexusmods.com/witcher3/mods/484\">https://www.nexusmods.com/witcher3/mods/484</a><br><br>"))
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec_()


def MessageAlertModFromGamePath(modPath, gamePath):
    message = QMessageBox(None)
    message.setIcon(QMessageBox.Information)
    message.setWindowTitle(
        TRANSLATE("MainWindow", "Invalid Mod Location"))
    message.setText(
        TRANSLATE("MainWindow", "Adding mods from within the game's directory is not supported.<br>" +
        "If you want to add existing mods to the manager you have to uninstall them first.<br><br>") +
        TRANSLATE("MainWindow", "Mod locaion: ") + modPath + "<br>" +
        TRANSLATE("MainWindow", "Game location: ") + gamePath + "<br><br>")
    message.setStandardButtons(QMessageBox.Ok)
    message.setTextFormat(Qt.RichText)
    return message.exec_()
