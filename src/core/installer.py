'''Core functionality'''
# pylint: disable=invalid-name,superfluous-parens,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring

from os import path, listdir, remove
from time import gmtime, strftime
from shutil import rmtree
from dataclasses import dataclass
from typing import Callable

from PyQt5.QtWidgets import QMessageBox
from src.globals import data
from src.util.util import *
from src.core.fetcher import *
from src.core.model import Model
from src.gui.alerts import MessageOverwrite
from src.globals.constants import TRANSLATE


@dataclass
class Installer:
    '''Mod Installer'''

    model: Model
    ask: bool = True
    progress: Callable[[float], any] = lambda _: None
    output: Callable[[str], any] = lambda _: None

    def installMod(self, modPath: str) -> bool:
        '''Installs mod from given path. If given mod is an archive first extracts it'''

        modname = path.split(modPath)[1]
        self.output(TRANSLATE("MainWindow", "Installing") + " " + Mod.formatName(modname))
        self.progress(0.1)
        mod = None
        try:
            mod, directories, xmls = fetchMod(modPath)
            installed_mods = listdir(data.config.mods)
            installed_dlcs = listdir(data.config.dlc)
            self.progress(0.2)
            res = None

            for index, directory in enumerate(directories):
                _, name = path.split(directory)
                basepath = data.config.mods if isDataFolder(name) else data.config.dlc
                datapath = basepath + "/" + name
                if (name in installed_mods) or (name in installed_dlcs):
                    if self.ask:
                        res = MessageOverwrite(name)
                    if res == QMessageBox.Yes:
                        files.rmtree(datapath)
                    elif res == QMessageBox.YesToAll:
                        files.rmtree(datapath)
                        self.ask = False
                    elif res == QMessageBox.NoToAll:
                        self.ask = False
                    elif res == QMessageBox.Cancel:
                        self.uninstallMod(mod)
                        return
                copyfolder(directory, datapath)
                self.progress(0.2 + (0.5 / len(directories)) * (index + 1))

            for xml in xmls:
                _, name = path.split(xml)
                files.copy(xml, data.config.menu+"/"+name)

            self.progress(0.8)
            if (not mod.files):
                raise Exception('No data foind in ' + "'"+mod.name+"'")

            mod.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            mod.name = modname
            mod.addXmlKeys()
            mod.addInputKeys()
            mod.addUserSettings()
            mod.checkPriority()

            self.progress(0.9)
            exists = False
            for installed in self.model.all():
                if mod.files == installed.files:
                    installed.usersettings = mod.usersettings
                    installed.hidden = mod.hidden
                    installed.xmlkeys = mod.xmlkeys
                    installed.dlcs = mod.dlcs
                    installed.date = mod.date
                    installed.menus = mod.menus
                    installed.inputsettings = mod.inputsettings
                    exists = True
                    break
            if not exists:
                self.model.add(mod.name, mod)

            self.progress(1.0)
            return True
        except Exception as err:
            self.output(formatUserError(err))
            if mod:
                self.uninstallMod(mod)
            return False
        finally:
            if path.exists(data.config.extracted):
                rmtree(data.config.extracted)

    def uninstallMod(self, mod: Mod) -> bool:
        '''Uninstalls given mod'''
        try:
            self.output(TRANSLATE("MainWindow", "Uninstalling") + " " + mod.name)
            if not mod.enabled:
                mod.enable()
            mod.removeXmlKeys()
            self.removeModMenus(mod)
            self.removeModDlcs(mod)
            self.removeModData(mod)
            self.model.remove(mod.name)
            return True
        except Exception as err:
            self.output(formatUserError(err))
            return False

    @staticmethod
    def removeModData(mod):
        '''Removes mod data'''
        for file in mod.files:
            if path.exists(data.config.mods + "/" + file):
                rmtree(data.config.mods + "/" + file)

    @staticmethod
    def removeModDlcs(mod):
        '''Removes dlc data'''
        for dlc in mod.dlcs:
            if path.exists(data.config.dlc + "/" + dlc):
                rmtree(data.config.dlc + "/" + dlc)

    @staticmethod
    def removeModMenus(mod):
        '''Removes menu data'''
        for menu in mod.menus:
            if path.exists(data.config.menu + "/" + menu):
                remove(data.config.menu + "/" + menu)
