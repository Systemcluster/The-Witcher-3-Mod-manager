'''Core functionality'''
# pylint: disable=invalid-name,superfluous-parens,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring

from os import path, listdir, walk, remove
from time import gmtime, strftime
from shutil import rmtree

from PyQt5.QtWidgets import QMessageBox

from src.domain.mod import Mod
from src.domain.key import Key
from src.globals import data
from src.util.util import *
from src.core.fetcher import *


def installMod(ui, modPath, progressStart, progressEnd):
    '''Installs mod from given path. If given mod is an archive first extracts it'''
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-nested-blocks

    progress = progressEnd - progressStart
    mod = Mod()
    installed = listdir(data.config.get('PATHS', 'mod'))
    try:
        _, modname = path.split(modPath)
        mod.setName(modname)
        mod.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if (isArchive(modPath)):
            modPath = extractArchive(modPath)

        ask = True
        ui.setProgress(progressStart + progress * 0.4)
        for subdir, drs, fls in walk(modPath):
            _, name = path.split(subdir)
            if ("content" in (dr.lower() for dr in drs)):
                if (re.match("^mod.*", name, re.IGNORECASE)):
                    if (name in installed and ask):
                        res = ui.MessageOverwrite(name)
                        if res == QMessageBox.Yes:
                            files.rmtree(data.config.get('PATHS', 'mod')+"/"+name)
                        elif res == QMessageBox.YesToAll:
                            files.rmtree(data.config.get('PATHS', 'mod')+"/"+name)
                            ask = False
                        elif res == QMessageBox.NoToAll:
                            ask = False
                        elif res == QMessageBox.Cancel:
                            uninstall(mod)
                            return
                    copyfolder(subdir, data.config.get('PATHS', 'mod')+"/"+name)
                    mod.files.append(name)
                else:
                    copyfolder(subdir, data.config.get('PATHS', 'dlc')+"/"+name)
                    mod.dlcs.append(name)
                if ("content" in drs):
                    drs.remove("content")
                elif "Content" in drs:
                    drs.remove("Content")
            for file in fls:
                if (re.match(r".*\.xml$", file) and not re.match(r"^input\.xml$", file)):
                    files.copy(subdir+"/"+file, data.config.get('PATHS', 'menu')+"/"+file)
                    mod.menus.append(file)
                elif(re.match(r"(.*\.txt)|(input\.xml)$", file)):
                    encodingWrong = True
                    encode = 'utf-8'
                    while(encodingWrong):
                        try:
                            if (encode == 'utf-16'):
                                encodingWrong = False
                            with open(subdir+"/"+file, 'r', encoding=encode) as myfile:
                                filetext = myfile.read()
                                encodingWrong = False

                                if (file == "input.xml"):
                                    temp = re.search(
                                        r'id="Hidden".+id="PCInput"',
                                        filetext,
                                        re.DOTALL)
                                    if (temp):
                                        hiddentext = temp.group(0)
                                        hiddentext = re.sub('<!--.*-->', '', hiddentext)
                                        hiddentext = re.sub(
                                            '<!--.*-->', '', hiddentext,
                                            0, re.DOTALL)
                                        xmlkeys = XMLPATTERN.findall(hiddentext)
                                        for key in xmlkeys:
                                            key = re.sub(r"\s+", " ", key)
                                            mod.hidden.append(key)

                                    temp = re.search(INPUT_XML_PATTERN, filetext, re.DOTALL)
                                    filetext = temp.group(0)
                                    filetext = re.sub('<!--.*-->', '', filetext)
                                    filetext = re.sub('<!--.*-->', '', filetext, 0, re.DOTALL)

                                xmlkeys = XMLPATTERN.findall(filetext)
                                if (xmlkeys):
                                    if ("hidden" in file):
                                        for key in xmlkeys:
                                            key = re.sub(r"\s+", " ", key)
                                            mod.hidden.append(key)
                                    else:
                                        for key in xmlkeys:
                                            key = re.sub(r"\s+", " ", key)
                                            mod.xmlkeys.append(key)

                                inputsettings = INPUTPATTERN.search(filetext)
                                if (inputsettings):
                                    res = re.sub(r"\n+", r"\n", inputsettings.group(0))
                                    arr = str(res).split('\n')
                                    if ('' in arr):
                                        arr.remove('')
                                    cntx = ''
                                    for key in arr:
                                        if (key[0] == "["):
                                            cntx = key
                                        else:
                                            newkey = Key(cntx, key)
                                            mod.inputsettings.append(newkey)

                                usersettings = USERPATTERN.search(filetext)
                                if (usersettings):
                                    res = re.sub(r"\n+", r"\n", usersettings.group(0))
                                    mod.usersettings.append(str(res))
                        except:
                            encode = 'utf-16'
        ui.setProgress(progressStart + progress * 0.7)
        if (not mod.files):
            raise Exception('No data foind in ' + "'"+mod.name+"'")
        mod.addXmlKeys()
        mod.addInputKeys(ui)
        mod.addUserSettings()
        mod.checkPriority()
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
        if (not exists):
            ui.addMod(mod.name, mod)
    except Exception as err:
        ui.output(formatUserError(err))
        uninstall(mod)


def uninstall(mod):
    '''Uninstalls given mod'''
    if (not mod.enabled):
        mod.enable()
    mod.removeXmlKeys()
    removeMenues(mod)
    removeDlcs(mod)
    removeData(mod)


def removeData(mod):
    '''Removes mod data'''
    for file in mod.files:
        if path.exists(data.config.get('PATHS', 'mod') + "/" + file):
            rmtree(data.config.get('PATHS', 'mod') + "/" + file)


def removeDlcs(mod):
    '''Removes dlc data'''
    for dlc in mod.dlcs:
        if path.exists(data.config.get('PATHS', 'dlc') + "/" + dlc):
            rmtree(data.config.get('PATHS', 'dlc') + "/" + dlc)


def removeMenues(mod):
    '''Removes menu data'''
    for menu in mod.menus:
        if path.exists(data.config.get('PATHS', 'menu') + "/" + menu):
            remove(data.config.get('PATHS', 'menu') + "/" + menu)
