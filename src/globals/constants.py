'''Global constants'''
# pylint: disable=invalid-name

from PySide6.QtCore import QCoreApplication

translate = QCoreApplication.translate

VERSION = "1.0-beta"
TITLE = translate("GLOBALS", "The Witcher 3 Mod Manager")
AUTHORS = ["Stefan Kostic (stefan3372)", "Christian Sdunek (Systemcluster)",
           "Adam Sunderman (madman asunder)", "Henry Hsieh (henry-hsieh)", "George Burduli (burdulixda)"]
AUTHORS_MAIL = ["stekos@live.com", "me@systemcluster.me",
                "amsunderman@gmail.com", "r901042004@yahoo.com.tw", "burduli01@pm.me"]

URL_WEB = "https://www.nexusmods.com/witcher3/mods/2678"
URL_GIT = "https://github.com/Systemcluster/The-Witcher-3-Mod-manager.git"
