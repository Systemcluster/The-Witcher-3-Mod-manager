import patoolib
import os.path as path
from PyQt5.Qt import *
from Helpers import *
from ModClass import Mod, Key
from time import gmtime, strftime

xmlpattern = re.compile("<Var.+\/>", re.UNICODE)
inputpattern = re.compile(r"(\[.*\]\s*(IK_.+=\(Action=.+\)\s*)+\s*)+", re.UNICODE)
userpattern = re.compile(r"(\[.*\]\s*(.*=(?!.*(\(|\))).*\s*)+)+", re.UNICODE)

def installMod(ui, modPath, pstart, pend):
    '''Installs mod from given path. if givem mod is archive it first extracts it'''
    progress = pend - pstart
    mod = Mod()
    installed = os.listdir(getini('PATHS', 'mod'))
    try:
        moddir, modname = path.split(modPath)
        mod.setName(modname)
        mod.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if (re.match(".+\.(zip|rar|7z)$",path.basename(modPath))):
            if(path.exists(manager + "/extracted")):
                files.rmtree(manager + "/extracted")
            os.mkdir(manager + "/extracted")
            patoolib.extract_archive(modPath, outdir=manager + "/extracted", verbosity=-1)
            modPath = manager + "/extracted"

        ask = True

        ui.setProgress(pstart + progress * 0.4)
        for subdir, drs, fls in os.walk(modPath):
            dir, name = path.split(subdir)
            if ("content" in (dr.lower() for dr in drs)):
                if (re.match("^mod.*", name, re.IGNORECASE)):
                    if (name in installed and ask):
                        res = ui.MessageOverwrite(name)
                        if res == QMessageBox.Cancel:
                            uninstall(mod)
                            return
                        elif res == QMessageBox.Yes:
                            files.rmtree(getini('PATHS', 'mod')+"/"+name)
                        elif res == QMessageBox.YesToAll:
                            files.rmtree(getini('PATHS', 'mod')+"/"+name)
                            ask = False
                        elif res == QMessageBox.NoToAll:
                            ask = False
                    copyfolder(subdir, getini('PATHS', 'mod')+"/"+name)
                    mod.files.append(name)
                else:
                    copyfolder(subdir, getini('PATHS', 'dlc')+"/"+name)
                    mod.dlcs.append(name)
                if ("content" in drs):
                    drs.remove("content")
                elif "Content" in drs:
                    drs.remove("Content")
            for file in fls:
                if (re.match(".*\.xml$", file) and not re.match("^input\.xml$", file)):
                    files.copy(subdir+"/"+file, getini('PATHS', 'menu')+"/"+file)
                    mod.menus.append(file)
                elif(re.match("(.*\.txt)|(input\.xml)$", file)):
                    encodingwrong = True
                    encode = 'utf-8'
                    while(encodingwrong):
                        try:
                            if (encode == 'utf-16'):
                                encodingwrong = False
                            with open(subdir+"/"+file, 'r', encoding=encode) as myfile:
                                filetext = myfile.read()
                                encodingwrong = False

                                if (file == "input.xml"):
                                    temp = re.search('id="Hidden".+id="PCInput"', filetext, re.DOTALL)
                                    hiddentext = temp.group(0)
                                    if (hiddentext):
                                        hiddentext = re.sub('<!--.*-->','',hiddentext)
                                        hiddentext = re.sub('<!--.*-->','',hiddentext,0,re.DOTALL)
                                        xmlkeys = xmlpattern.findall(hiddentext)
                                        for key in xmlkeys:
                                            key = re.sub("\s+", " ", key)
                                            mod.hidden.append(key)

                                    temp = re.search('id="PCInput".+<!--\s*\[BASE_CharacterMovement\]\s*-->', filetext, re.DOTALL)
                                    filetext = temp.group(0)
                                    filetext = re.sub('<!--.*-->','',filetext)
                                    filetext = re.sub('<!--.*-->','',filetext,0,re.DOTALL)

                                xmlkeys = xmlpattern.findall(filetext)
                                if (xmlkeys):
                                    if ("hidden" in file):
                                        for key in xmlkeys:
                                            key = re.sub("\s+", " ", key)
                                            mod.hidden.append(key)
                                    else:
                                        for key in xmlkeys:
                                            key = re.sub("\s+", " ", key)
                                            mod.xmlkeys.append(key)

                                inputsettings = inputpattern.search(filetext)
                                if (inputsettings):
                                    res = re.sub("\n+","\n",inputsettings.group(0))
                                    arr = str(res).split('\n')
                                    if ('' in arr):
                                        arr.remove('')
                                    cntx = ''
                                    for key in arr:
                                        if (key[0] == "["):
                                            cntx = key
                                        else:
                                            newkey = Key()
                                            newkey.populate(cntx, key)
                                            mod.inputsettings.append(newkey)

                                usersettings = userpattern.search(filetext)
                                if (usersettings):
                                    res = re.sub("\n+","\n",usersettings.group(0))
                                    mod.usersettings.append(str(res))
                        except:
                            encode = 'utf-16'
        ui.setProgress(pstart + progress * 0.7)
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
    except Exception as er:
        ui.output(str(er))
        uninstall(mod)

def uninstall(mod):
    '''Uninstalls given mod'''
    if (not mod.enabled):
        mod.enable()
    mod.removeXmlKeys()
    for menu in mod.menus:
        if path.exists(getini('PATHS', 'menu')+"/"+menu):
            os.remove(getini('PATHS', 'menu')+"/"+menu)
    for dlc in mod.dlcs:
        if path.exists(getini('PATHS', 'dlc')+"/"+dlc):
            files.rmtree(getini('PATHS', 'dlc')+"/"+dlc)
    for data in mod.files:
        if path.exists(getini('PATHS', 'mod')+"/"+data):
            files.rmtree(getini('PATHS', 'mod')+"/"+data)
