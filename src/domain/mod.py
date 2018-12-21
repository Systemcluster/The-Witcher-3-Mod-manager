'''Mod Class'''
#pylint: disable=invalid-name,wildcard-import,unused-wildcard-import,superfluous-parens

import re
from os import path, rename, walk
from dataclasses import dataclass

from PyQt5.Qt import QMessageBox

from src.util.util import *
from src.domain.key import Key

@dataclass
class Mod:
    '''Mod objects containing all mod data'''

    name: ''
    files: []
    dlcs: []
    menus: []
    xmlkeys: []
    usersettings: []
    inputsettings: []
    hidden: []
    enabled: True
    date: '-'
    priority: None

    def getPriority(self):
        if(self.priority is None):
            return '-'
        else:
            return str(self.priority)
    def setPriority(self, value):
        for data in self.files:
            setpriority(data, value)
        self.priority = str(value)
    def setName(self, name):
        if (re.match("^mod.*", name)):
            name = name[3:]
        lenght = len(name)
        for match in re.finditer(r"-[0-9]+-.+", name):
            lenght = match.span()[0]
        name = name[0:lenght]
        if (re.search(r".*\.(zip|rar)$", name)):
            name = name[:-4]
        elif (re.search(r".*\.7z$", name)):
            name = name[:-3]
        self.name = name
    def enable(self):
        if (not self.enabled):
            self.addXmlKeys()
            for menu in self.menus:
                if path.exists(getini('PATHS', 'menu') + "/" + menu + ".disabled"):
                    rename(
                        getini('PATHS', 'menu') + "/" + menu + ".disabled",
                        getini('PATHS', 'menu') + "/" + menu)
            for dlc in self.dlcs:
                if path.exists(getini('PATHS', 'dlc') + "/" + dlc):
                    for subdir, _, fls in walk(getini('PATHS', 'dlc') + "/" + dlc):
                        for file in fls:
                            if (path.exists(subdir + "/" + file)):
                                rename(subdir + "/" + file, subdir + "/" + file[:-9])
            for data in self.files:
                if path.exists(getini('PATHS', 'mod') + "/~" + data):
                    rename(
                        getini('PATHS', 'mod') + "/~" + data,
                        getini('PATHS', 'mod') + "/" + data)
            self.enabled = True
    def disable(self):
        if (self.enabled):
            self.removeXmlKeys()
            for menu in self.menus:
                if path.exists(getini('PATHS', 'menu') + "/" + menu):
                    rename(
                        getini('PATHS', 'menu') + "/" + menu,
                        getini('PATHS', 'menu') + "/" + menu + ".disabled")
            for dlc in self.dlcs:
                if path.exists(getini('PATHS', 'dlc') + "/" + dlc):
                    for subdir, _, fls in walk(getini('PATHS', 'dlc') + "/" + dlc):
                        for file in fls:
                            rename(
                                path.join(subdir, file),
                                path.join(subdir, file) + ".disabled")
            for data in self.files:
                if path.exists(getini('PATHS', 'mod') + "/" + data):
                    rename(
                        getini('PATHS', 'mod') + "/" + data,
                        getini('PATHS', 'mod') + "/~" + data)
            self.enabled = False
    def populateFromXml(self, root):
        self.date = root.get('date')
        enabled = root.get('enabled')
        if (enabled == 'True'):
            self.enabled = True
        else:
            self.enabled = False
        self.name = root.get('name')
        prt = root.get('priority')
        if (not prt == 'Not Set'):
            self.priority = prt
        for data in root.findall('data'):
            self.files.append(data.text)
        for data in root.findall('dlc'):
            self.dlcs.append(data.text)
        for data in root.findall('menu'):
            self.menus.append(data.text)
        for data in root.findall('xmlkey'):
            self.xmlkeys.append(data.text)
        for data in root.findall('hidden'):
            self.hidden.append(data.text)
        for data in root.findall('key'):
            key = Key(data.get('context'), data.text)
            self.inputsettings.append(key)
        for data in root.findall('settings'):
            self.usersettings.append(data.text)
        self.checkPriority()
    def checkPriority(self):
        if (not self.priority):
            for data in self.files:
                if (priority.has_section(data)):
                    self.setPriority(priority.get(data, 'Priority'))
    def writeToXml(self, root):
        mod = XML.SubElement(root, 'mod')
        mod.set('name', self.name)
        mod.set('enabled', str(self.enabled))
        mod.set('date', self.date)
        mod.set('priority', self.getPriority())
        if (self.files):
            for file in self.files:
                XML.SubElement(mod, 'data').text = file
        if (self.dlcs):
            for dlc in self.dlcs:
                XML.SubElement(mod, 'dlc').text = dlc
        if (self.menus):
            for menu in self.menus:
                XML.SubElement(mod, 'menu').text = menu
        if (self.xmlkeys):
            for xml in self.xmlkeys:
                XML.SubElement(mod, 'xmlkey').text = xml
        if (self.hidden):
            for xml in self.hidden:
                XML.SubElement(mod, 'hidden').text = xml
        if (self.inputsettings):
            for key in self.inputsettings:
                ky = XML.SubElement(mod, 'key')
                ky.text = str(key)
                ky.set('context', key.context)
        if (self.usersettings):
            XML.SubElement(mod, 'settings').text = self.usersettings[0]
        return root
    def addXmlKeys(self):
        if (self.xmlkeys):
            text = ''
            with open(getini('PATHS', 'menu') + "/input.xml", 'r') as userfile:
                text = userfile.read()
            for xml in self.xmlkeys:
                if (not xml in text):
                    text = text.replace(
                        '<!-- [BASE_CharacterMovement] -->',
                        xml+'\n<!-- [BASE_CharacterMovement] -->')
            with open(getini('PATHS', 'menu') + "/input.xml", 'w') as userfile:
                text = userfile.write(text)
        if (self.hidden):
            text = ''
            with open(getini('PATHS', 'menu') + "/hidden.xml", 'r') as userfile:
                text = userfile.read()
            for xml in self.hidden:
                if (not xml in text):
                    text = text.replace(
                        '</VisibleVars>',
                        xml+'\n</VisibleVars>')
            with open(getini('PATHS', 'menu') + "/hidden.xml", 'w') as userfile:
                text = userfile.write(text)
    def addInputKeys(self, ui):
        added = 0
        if (self.inputsettings):
            text = ''
            with open(getini('PATHS', 'settings') + "/input.settings", 'r') as userfile:
                text = userfile.read()
            ask = True
            keep = True
            for key in self.inputsettings:
                keycontext = key.context[1:-1]
                context = re.search(r"\[" + keycontext + r"\]\n(.+\n)+", text)
                if (not context):
                    text = '['+keycontext+']\n\n' + text
                    contexttext = '['+keycontext+']\n'
                else:
                    contexttext = str(context.group(0))
                if (key.duration or key.axis):
                    foundkeys = re.findall(r".*Action="+key.action+r",.*", contexttext)
                else:
                    foundkeys = re.findall(r".*Action="+key.action+r"\)", contexttext)
                if (not foundkeys):
                    added += 1
                    text = re.sub(
                        r"\[" + keycontext + r"\]\n",
                        r"[" + keycontext + r"]\n"+str(key)+"\n",
                        text)
                else:
                    shdadd = True
                    for foundkey in foundkeys:
                        if (foundkey == str(key)):
                            shdadd = False
                            break
                    if (shdadd):
                        for foundkey in foundkeys:
                            temp = Key('', foundkey)
                            if (temp.type == key.type and temp.axis == key.axis and
                                    temp.duration == key.duration):
                                shdadd = False
                                if (ask):
                                    msg = ui.MessageRebindedKeys(key, temp)
                                    if msg == QMessageBox.SaveAll:
                                        shdadd = True
                                        break
                                    elif msg == QMessageBox.Yes:
                                        keep = True
                                    elif msg == QMessageBox.No:
                                        keep = False
                                    elif msg == QMessageBox.YesToAll:
                                        ask = False
                                        keep = True
                                    elif msg == QMessageBox.NoToAll:
                                        ask = False
                                        keep = False
                                    else:
                                        keep = True
                                if (not keep):
                                    newcontexttext = contexttext.replace(foundkey, str(key))
                                    text = text.replace(contexttext, newcontexttext)
                                    contexttext = newcontexttext
                        if (shdadd):
                            added += 1
                            text = re.sub(
                                r"\[" + keycontext + r"\]\n",
                                r"[" + keycontext + r"]\n" + str(key) + r"\n",
                                text)
            with open(getini('PATHS', 'settings') + "/input.settings", 'w') as userfile:
                text = userfile.write(text)
    def addUserSettings(self):
        if (self.usersettings):
            text = ''
            with open(getini('PATHS', 'settings') + "/user.settings", 'r') as userfile:
                text = userfile.read()
            with open(getini('PATHS', 'settings')+"/user.settings", 'w') as userfile:
                text = self.usersettings[0] + "\n" + text
                userfile.write(text)
    def removeXmlKeys(self):
        if (self.xmlkeys):
            text = ''
            with open(getini('PATHS', 'menu') + "/input.xml", 'r') as userfile:
                text = userfile.read()
            for xml in self.xmlkeys:
                if xml in text:
                    text = text.replace(xml+"\n", '')
            with open(getini('PATHS', 'menu') + "/input.xml", 'w') as userfile:
                text = userfile.write(text)
        if (self.hidden):
            text = ''
            with open(getini('PATHS', 'menu') + "/hidden.xml", 'r') as userfile:
                text = userfile.read()
            for xml in self.hidden:
                if xml in text:
                    text = text.replace(xml+"\n", '')
            with open(getini('PATHS', 'menu') + "/hidden.xml", 'w') as userfile:
                text = userfile.write(text)
    def __str__(self):
        string = "NAME: " + str(self.name) + "\nENABLED: " + str(self.enabled) + \
            "\nPRIORITY: " + self.getPriority() + "\n"
        if (self.files):
            string += "\nDATA:\n"
            for file in self.files:
                string += file + "\n"
        if (self.dlcs):
            string += "\nDLC:\n"
            for dlc in self.dlcs:
                string += dlc + "\n"
        if (self.menus):
            string += "\nMENUS:\n"
            for menu in self.menus:
                string += menu + "\n"
        if (self.xmlkeys):
            string += "\nXML VARIABLES:\n"
            for xml in self.xmlkeys:
                string += xml + "\n"
        if (self.hidden):
            string += "\nHIDDEN XML:\n"
            for xml in self.hidden:
                string += xml + "\n"
        if (self.inputsettings):
            string += "\nINPUT KEYS:\n"
            context = ''
            for key in self.inputsettings:
                if (key.context != context):
                    if (context != ''):
                        string += '\n'
                    context = key.context
                    string += context + '\n'
                string += str(key) + "\n"

        if (self.usersettings):
            string += "\nUSER SETTINGS:\n"
            string += self.usersettings[0] + "\n"
        return string
