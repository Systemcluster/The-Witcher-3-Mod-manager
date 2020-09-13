'''Core functionality'''
# pylint: disable=invalid-name,superfluous-parens,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring

from os import path, listdir, remove, mkdir
from time import gmtime, strftime
from shutil import rmtree, copyfile
from dataclasses import dataclass
from typing import Callable, Any

from PySide2.QtWidgets import QMessageBox
from src.globals import data
from src.util.util import *
from src.core.fetcher import *
from src.core.model import Model
from src.gui.alerts import MessageAlertModFromGamePath, MessageOverwrite
from src.globals.constants import TRANSLATE


@dataclass
class Installer:
    '''Mod Installer'''

    model: Model
    ask: bool = True

    progress: Callable[[float], Any] = lambda _: None
    output: Callable[[str], Any] = lambda _: None

    def installMod(self, modPath: str) -> Tuple[bool, int]:
        '''Installs mod from given path. If given mod is an archive first extracts it'''

        if os.path.realpath(modPath).startswith(os.path.realpath(data.config.game)):
            MessageAlertModFromGamePath()
            return False, 0

        installCount = 0
        modname = path.split(modPath)[1]
        self.output(TRANSLATE("MainWindow", "Installing") +
                    " " + Mod.formatName(modname))
        self.progress(0.1)
        mod = None
        result = True
        try:
            mod, directories, xmls = fetchMod(modPath)

            mod.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            mod.name = modname

            if not path.isdir(data.config.mods):
                mkdir(data.config.mods)
            if not path.isdir(data.config.dlc):
                mkdir(data.config.dlc)
            installed_mods = listdir(data.config.mods)
            installed_dlcs = listdir(data.config.dlc)

            self.progress(0.2)
            res = None

            for index, directory in enumerate(directories):
                root, name = path.split(directory)
                _, parent = path.split(root)
                modfolder = isModFolder(name, parent)
                dlcfolder = isDlcFolder(name, parent)
                basepath = data.config.mods if modfolder else (
                    data.config.dlc if dlcfolder else None)
                if basepath is not None:
                    datapath = basepath + "/" + name
                    if (modfolder and name in installed_mods) or (dlcfolder and name in installed_dlcs):
                        if self.ask:
                            res = MessageOverwrite(
                                name, 'Mod' if modfolder else 'DLC')
                        if res == QMessageBox.Yes:
                            copyFolder(directory, datapath)
                            installCount += 1
                        elif res == QMessageBox.YesToAll:
                            self.ask = False
                            copyFolder(directory, datapath)
                            installCount += 1
                        elif res == QMessageBox.No:
                            pass
                        elif res == QMessageBox.NoToAll:
                            self.ask = False
                    else:
                        copyFolder(directory, datapath)
                        installCount += 1
                elif containContentFolder(directory):
                    try:
                        ddir = directory[len(data.config.extracted)+1:]
                    except:
                        ddir = ''
                    self.output(
                        f"Detected data folder but could not recognize it as part of a mod or dlc{': '+ddir if ddir else ''}")
                    self.output(
                        f"  Some manual installation may be required, please check the mod to make sure.")
                self.progress(0.2 + (0.5 / len(directories)) * (index + 1))

            for xml in xmls:
                _, name = path.split(xml)
                if not path.isdir(data.config.menu):
                    os.makedirs(data.config.menu)
                copyfile(xml, data.config.menu+"/"+name)

            self.progress(0.8)

            if (not mod.files and not mod.dlcs):
                raise Exception('No data found in ' + "'"+mod.name+"'")

            mod.installXmlKeys()
            mod.installInputKeys()
            mod.installUserSettings()
            mod.checkPriority()

            if mod.readmes:
                self.output("Detected one or more README files.")
                self.output(
                    f"  Some manual configuration may be required, please read the readme to make sure.")

            self.progress(0.9)
            exists = False
            for installed in self.model.all():
                if mod.files == installed.files and mod.name == installed.name:
                    installed.usersettings = mod.usersettings
                    installed.hidden = mod.hidden
                    installed.xmlkeys = mod.xmlkeys
                    installed.dlcs = mod.dlcs
                    installed.date = mod.date
                    installed.menus = mod.menus
                    installed.inputsettings = mod.inputsettings
                    installed.readmes = mod.readmes
                    exists = True
                    break
            if not exists:
                self.model.add(mod.name, mod)

            self.progress(1.0)
            result = True
        except Exception as err:
            self.output(formatUserError(err))
            if mod:
                self.uninstallMod(mod)
            result = False
            installCount = 0
        finally:
            if path.exists(data.config.extracted):
                rmtree(data.config.extracted)
        return result, installCount

    def uninstallMod(self, mod: Mod) -> bool:
        '''Uninstalls given mod'''
        try:
            self.output(
                TRANSLATE("MainWindow", "Uninstalling") + " " + mod.name)
            if not mod.enabled:
                mod.enable()
            mod.uninstallXmlKeys()
            mod.uninstallUserSettings()
            self.removeModMenus(mod)
            self.removeModDlcs(mod)
            self.removeModData(mod)
            self.model.remove(mod.name)
            return True
        except Exception as err:
            self.output(formatUserError(err))
            return False

    def reinstallMod(self, mod: Mod) -> bool:
        try:
            self.output(
                TRANSLATE("MainWindow", "Reinstalling") + " " + mod.name)
            if not mod.enabled:
                mod.enable()
            mod.uninstallUserSettings()
            mod.installUserSettings()
            mod.uninstallXmlKeys()
            mod.installXmlKeys()
            mod.installInputKeys()
            # TODO: re-fetch and copy xml files
            return True
        except Exception as err:
            self.output(formatUserError(err))
            return False

    def removeModData(self, mod):
        '''Removes mod data'''
        for file in mod.files:
            if path.exists(data.config.mods + "/" + file):
                rmtree(data.config.mods + "/" + file)

    def removeModDlcs(self, mod):
        '''Removes dlc data'''
        for dlc in mod.dlcs:
            if path.exists(data.config.dlc + "/" + dlc):
                rmtree(data.config.dlc + "/" + dlc)

    def removeModMenus(self, mod):
        '''Removes menu data'''
        for menu in mod.menus:
            if path.exists(data.config.menu + "/" + menu):
                if menu in ("audio.xml", "gameplay.xml", "hidden.xml", "hud.xml", "input.xml", "localization.xml", "postprocess.xml", "rendering.xml"):
                    self.output("Note: Additions to " +
                                menu + " will not be removed.")
                else:
                    remove(data.config.menu + "/" + menu)
