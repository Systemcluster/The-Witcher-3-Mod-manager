'''Core functionality'''
# pylint: disable=invalid-name,superfluous-parens,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring

from os import path, listdir, remove
from time import gmtime, strftime
from shutil import rmtree

from PyQt5.QtWidgets import QMessageBox
from src.globals import data
from src.util.util import *
from src.core.fetcher import *
from src.gui.main_widget import CustomMainWidget
from src.gui.alerts import MessageOverwrite
from src.globals.constants import TRANSLATE


def install(modPath: str, ui: CustomMainWidget = None,
            progressStart: int = 0, progressEnd: int = 0):
    '''Installs mod from given path. If given mod is an archive first extracts it'''
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-nested-blocks

    modname = path.split(modPath)[1]
    progress = progressEnd - progressStart
    if ui:
        ui.output(TRANSLATE("MainWindow", "Installing") + " " + Mod.formatName(modname))
        ui.setProgress(progressStart + progress * 0.1)
    mod = None
    try:
        mod, directories, xmls = fetchMod(modPath)
        installed_mods = listdir(data.config.mods)
        installed_dlcs = listdir(data.config.dlc)
        if ui:
            ask = True
            ui.setProgress(progressStart + progress * 0.3)
        else:
            ask = False

        for directory in directories:
            _, name = path.split(directory)
            category = "mod" if isDataFolder(name) else "dlc"
            if (name in installed_mods and ask) or (name in installed_dlcs and ask):
                res = MessageOverwrite(name)
                if res == QMessageBox.Yes:
                    files.rmtree(data.config.get('PATHS', category)+"/"+name)
                elif res == QMessageBox.YesToAll:
                    files.rmtree(data.config.get('PATHS', category)+"/"+name)
                    ask = False
                elif res == QMessageBox.NoToAll:
                    ask = False
                elif res == QMessageBox.Cancel:
                    uninstall(mod)
                    return
            copyfolder(directory, data.config.get('PATHS', category)+"/"+name)

        for xml in xmls:
            _, name = path.split(xml)
            files.copy(xml, data.config.menu+"/"+name)

        if ui:
            ui.setProgress(progressStart + progress * 0.7)
        if (not mod.files):
            raise Exception('No data foind in ' + "'"+mod.name+"'")

        mod.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        mod.setName(modname)
        mod.addXmlKeys()
        mod.addInputKeys()
        mod.addUserSettings()
        mod.checkPriority()

        if ui:
            ui.setProgress(progressStart + progress * 0.85)
        exists = False
        for installed in ui.modList.values():
            if (mod.files == installed.files):
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
            if ui:
                ui.addMod(mod.name, mod)
        if ui:
            ui.setProgress(progressStart + progress * 1.0)
    except Exception as err:
        if ui:
            ui.output(formatUserError(err))
        else:
            formatUserError(err)
        if mod:
            uninstall(mod)
    finally:
        if (path.exists(data.config.extracted)):
            rmtree(data.config.extracted)

def uninstall(mod: Mod, ui: CustomMainWidget = None):
    '''Uninstalls given mod'''
    if ui:
        ui.output(TRANSLATE("MainWindow", "Uninstalling") + " " + mod.name)
    if not mod.enabled:
        mod.enable()
    mod.removeXmlKeys()
    removeMenues(mod)
    removeDlcs(mod)
    removeData(mod)


def removeData(mod):
    '''Removes mod data'''
    for file in mod.files:
        if path.exists(data.config.mods + "/" + file):
            rmtree(data.config.mods + "/" + file)


def removeDlcs(mod):
    '''Removes dlc data'''
    for dlc in mod.dlcs:
        if path.exists(data.config.dlc + "/" + dlc):
            rmtree(data.config.dlc + "/" + dlc)


def removeMenues(mod):
    '''Removes menu data'''
    for menu in mod.menus:
        if path.exists(data.config.menu + "/" + menu):
            remove(data.config.menu + "/" + menu)
