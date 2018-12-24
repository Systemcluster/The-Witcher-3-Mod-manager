'''Alert Dialogs'''
# pylint: disable=invalid-name

from PyQt5.QtWidgets import QMessageBox

from src.globals.constants import TRANSLATE


def MessageRebindedKeys(key, temp):
    '''Shows dialog to let user decide what to do if rebinded key is found'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Rebinded key found"),
        TRANSLATE("MainWindow", "Rebinded key found") + "\n" + \
            TRANSLATE("MainWindow", "Original key") + ": \n" + str(key) + "\n" + \
            TRANSLATE("MainWindow", "Current key") + ": " + str(temp) + "\n\n" + \
            TRANSLATE("MainWindow", "Do you wish to keep your current key?"),
        QMessageBox.Yes | QMessageBox.YesToAll | \
        QMessageBox.No | QMessageBox.NoToAll | QMessageBox.SaveAll,
        QMessageBox.Yes)

def MessageOverwrite(modname):
    '''Shows dialog to let user decide what to do if mod is already installed'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Mod allready installed"),
        "'" + modname + "' " + TRANSLATE(
            "MainWindow",
            "is already installed\nDo you want to remove old one first?"),
        QMessageBox.Yes | QMessageBox.YesToAll | \
            QMessageBox.No | QMessageBox.NoToAll | QMessageBox.Cancel,
        QMessageBox.No)

def MessageAlertScript():
    '''Shows dialog to let user know he/she should run script merger \
        after each change in the mod list'''
    return QMessageBox.question(
        None,
        TRANSLATE("MainWindow", "Run Script Merger"),
        TRANSLATE(
            "MainWindow",
            "After changing the mod list in any way you should run script merger to merge "+\
                "the mods and ensure their compatibility and remove previously merged scripts\n"
            "Do you want to run it now?\n"
            "\n"
            "Note: You can disable these alerts in the settings..."),
        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
