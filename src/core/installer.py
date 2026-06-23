'''Core functionality'''
# pylint: disable=invalid-name,superfluous-parens,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring

from dataclasses import dataclass
from os import listdir, mkdir, path, remove
from shutil import copyfile
from time import gmtime, strftime
from typing import Any, Callable

from PySide6.QtWidgets import QMessageBox

from src.core.fetcher import *
from src.core.model import Model
from src.globals import data
from src.globals.constants import translate
from src.gui.alerts import MessageAlertModFromGamePath, MessageOverwrite
from src.util.util import *


@dataclass
class Installer:
    '''Mod Installer'''

    model: Model
    ask: bool = True

    progress: Callable[[float], Any] = lambda _: None
    output: Callable[[str], Any] = lambda _: None

    def installMod(self, modPath: str) -> Tuple[bool, int, int]:
        '''Installs mod from given path. If given mod is an archive first extracts it'''

        realModPath = os.path.realpath(modPath)
        realGamePath = os.path.realpath(data.config.game)
        if realModPath and realGamePath and realModPath.startswith(realGamePath):
            MessageAlertModFromGamePath(realModPath, realGamePath)
            return False, 0, 0

        installCount = 0
        incompleteCount = 0
        modname = path.split(modPath)[1]
        self.output(translate("MainWindow", "Installing") +
                    " " + Mod.formatName(modname))
        self.progress(0.1)
        mod = None
        result = True
        try:
            mod, directories, xmls = fetchMod(modPath)

            mod.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            mod.name = modname

            if not data.config.mods:
                raise Exception(
                    translate("MainWindow", "Mods folder does not exist and could not be created."))
            if not data.config.dlc:
                raise Exception(
                    translate("MainWindow", "DLC folder does not exist and could not be created."))

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
                                name, translate("MainWindow", 'Mod') if modfolder else translate("MainWindow", 'DLC'))
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
                        translate("MainWindow", "Detected data folder but could not recognize it as part of a mod or dlc: ") + f"{ddir}")
                    self.output(
                        translate("MainWindow", "  Some manual installation may be required, please check the mod to make sure."))
                self.progress(0.2 + (0.5 / len(directories)) * (index + 1))

            for xml in xmls:
                _, name = path.split(xml)
                if not path.isdir(data.config.menu):
                    os.makedirs(data.config.menu)
                copyfile(xml, data.config.menu+"/"+name)

            self.progress(0.8)

            if (not mod.files and not mod.dlcs):
                raise Exception('No data found in ' + "'"+mod.name+"'")

            incomplete = False
            try:
                mod.installMenus()
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            translate("MainWindow", "menu xml files") + translate("MainWindow", " could not be automatically installed."))
            try:
                mod.installXmlKeys()
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            "input.xml" + translate("MainWindow", " could not be automatically installed."))
            try:
                added, skipped = mod.installInputKeys()
                self.output(
                    translate("MainWindow", "Added") + f" {added} " + translate("MainWindow", "input keys") +
                    (f" ({translate('MainWindow', 'skipped')} {skipped})" if skipped > 0 else ""))
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            "input.settings" + translate("MainWindow", " could not be automatically installed."))
            try:
                mod.installUserSettings()
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            "user.settings" + translate("MainWindow", " could not be automatically installed."))
            mod.checkPriority()

            if incomplete:
                incompleteCount += 1

            if mod.readmes:
                self.output(
                    translate("MainWindow", "Detected one or more README files."))
                self.output(
                    translate("MainWindow", "  Some manual configuration may be required, please read the readme to make sure."))

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
                removeDirectory(data.config.extracted)
        return result, installCount, incompleteCount

    def uninstallMod(self, mod: Mod) -> bool:
        '''Uninstalls given mod'''
        try:
            self.output(
                translate("MainWindow", "Uninstalling") + " " + mod.name)
            if not mod.enabled:
                incomplete = mod.enable()
                if incomplete:
                    for i in incomplete:
                        self.output(translate("MainWindow", "Note: Additions to ") +
                                    i + translate("MainWindow", " could not be automatically installed."))
            mod.uninstallMenus()
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

    def reinstallMod(self, mod: Mod) -> Tuple[bool, bool]:
        try:
            self.output(
                translate("MainWindow", "Reinstalling") + " " + mod.name)
            if not mod.enabled:
                incomplete = mod.enable()
                if incomplete:
                    for i in incomplete:
                        self.output(translate("MainWindow", "Note: Additions to ") +
                                    i + translate("MainWindow", " could not be automatically installed."))
            incomplete = False
            mod.uninstallUserSettings()
            try:
                mod.installUserSettings()
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            "user.settings" + translate("MainWindow", " could not be automatically installed."))
            mod.uninstallXmlKeys()
            try:
                mod.installXmlKeys()
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            "input.xml" + translate("MainWindow", " could not be automatically installed."))
            mod.uninstallMenus()
            try:
                mod.installMenus()
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            translate("MainWindow", "menu xml files") + translate("MainWindow", " could not be automatically installed."))
            try:
                added, skipped = mod.installInputKeys()
                self.output(
                    translate("MainWindow", "Added") + f" {added} " + translate("MainWindow", "input keys") +
                    (f" ({translate('MainWindow', 'skipped')} {skipped})" if skipped > 0 else ""))
            except Exception as err:
                incomplete = True
                self.output(formatUserError(err))
                self.output(translate("MainWindow", "Note: Additions to ") +
                            "input.settings" + translate("MainWindow", " could not be automatically installed."))
            # TODO: re-fetch and copy xml files
            return (True, incomplete)
        except Exception as err:
            self.output(formatUserError(err))
            return (False, False)

    def removeModData(self, mod):
        '''Removes mod data'''
        if not data.config.mods or not path.exists(data.config.mods):
            return
        for file in mod.files:
            if path.exists(data.config.mods + "/" + file):
                removeDirectory(data.config.mods + "/" + file)

    def removeModDlcs(self, mod):
        '''Removes dlc data'''
        if not data.config.dlc or not path.exists(data.config.dlc):
            return
        for dlc in mod.dlcs:
            if path.exists(data.config.dlc + "/" + dlc):
                removeDirectory(data.config.dlc + "/" + dlc)

    def removeModMenus(self, mod):
        '''Removes menu data'''
        if not data.config.menu or not path.exists(data.config.menu):
            return
        for menu in mod.menus:
            if path.exists(data.config.menu + "/" + menu):
                if menu in ("audio.xml", "display.xml", "dx11filelist.txt", "dx12filelist.txt", "gameplay.xml", "gamma.xml", "graphics.xml", "graphicsdx11.xml", "hidden.xml", "hud.xml", "input.xml", "localization.xml", "postprocess.xml", "rendering.xml"):
                    self.output(translate("MainWindow", "Note: Additions to ") +
                                menu + translate("MainWindow", " will not be removed."))
                else:
                    remove(data.config.menu + "/" + menu)
