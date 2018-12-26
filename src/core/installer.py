'''Core functionality'''
# pylint: disable=invalid-name,superfluous-parens,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring

from os import path, listdir, remove
from time import gmtime, strftime
from shutil import rmtree

from PyQt5.QtWidgets import QMessageBox
from src.globals import data
from src.util.util import *
from src.core.fetcher import *
from src.core.model import Model
from src.gui.main_widget import CustomMainWidget
from src.gui.alerts import MessageOverwrite
from src.globals.constants import TRANSLATE


def installMod(modPath: str, model: Model, ui: CustomMainWidget = None, \
                progressStart: int = 0, progressEnd: int = 0):
    '''Installs mod from given path. If given mod is an archive first extracts it'''

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
        res = None

        for directory in directories:
            _, name = path.split(directory)
            basepath = data.config.mods if isDataFolder(name) else data.config.dlc
            datapath = basepath + "/" + name
            if (name in installed_mods) or (name in installed_dlcs):
                if ask:
                    res = MessageOverwrite(name)

                if res == QMessageBox.Yes:
                    files.rmtree(datapath)
                elif res == QMessageBox.YesToAll:
                    files.rmtree(datapath)
                    ask = False
                elif res == QMessageBox.NoToAll:
                    ask = False
                elif res == QMessageBox.Cancel:
                    uninstallMod(mod, model, ui)
                    return

            copyfolder(directory, datapath)

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
        for installed in model.all():
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
            model.add(mod.name, mod)
        if ui:
            ui.setProgress(progressStart + progress * 1.0)
    except Exception as err:
        if ui:
            ui.output(formatUserError(err))
        else:
            formatUserError(err)
        if mod:
            uninstallMod(mod, model, ui)
    finally:
        if path.exists(data.config.extracted):
            rmtree(data.config.extracted)

def uninstallMod(mod: Mod, model: Model, ui: CustomMainWidget = None):
    '''Uninstalls given mod'''
    try:
        if ui:
            ui.output(TRANSLATE("MainWindow", "Uninstalling") + " " + mod.name)
        if not mod.enabled:
            mod.enable()
        mod.removeXmlKeys()
        removeModMenus(mod)
        removeModDlcs(mod)
        removeModData(mod)
        model.remove(mod.name)
    except Exception as err:
        if ui:
            ui.output(formatUserError(err))
        else:
            formatUserError(err)

def removeModData(mod):
    '''Removes mod data'''
    for file in mod.files:
        if path.exists(data.config.mods + "/" + file):
            rmtree(data.config.mods + "/" + file)

def removeModDlcs(mod):
    '''Removes dlc data'''
    for dlc in mod.dlcs:
        if path.exists(data.config.dlc + "/" + dlc):
            rmtree(data.config.dlc + "/" + dlc)

def removeModMenus(mod):
    '''Removes menu data'''
    for menu in mod.menus:
        if path.exists(data.config.menu + "/" + menu):
            remove(data.config.menu + "/" + menu)
