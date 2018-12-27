'''Mod Class'''
# pylint: disable=invalid-name,wildcard-import,unused-wildcard-import,superfluous-parens,missing-docstring

import re
from os import path, rename, walk
from time import strftime, gmtime
from dataclasses import dataclass, field
from typing import Union, List

from PyQt5.Qt import QMessageBox

from src.util.util import *
from src.domain.key import Key
from src.globals import data
from src.gui.alerts import MessageRebindedKeys

@dataclass
class Mod:
    '''Mod object containing all mod data'''

    _name: str = ''
    _priority: str = ''
    enabled: bool = True
    date: str = ''
    source: str = ''

    files: List[str] = field(default_factory=list)
    dlcs: List[str] = field(default_factory=list)
    menus: List[str] = field(default_factory=list)
    xmlkeys: List[str] = field(default_factory=list)
    usersettings: List[str] = field(default_factory=list)
    inputsettings: List[object] = field(default_factory=list)
    hidden: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, value: str) -> None:
        self._name = self.formatName(value)

    @property
    def priority(self) -> str:
        return self._priority if self._priority else '-'
    @priority.setter
    def priority(self, value: Union[str, int, None]):
        if value is None or not str(value).isdecimal():
            for modfile in iter(self.files):
                data.config.removePriority(modfile)
            self._priority = None
        else:
            for filedata in iter(self.files):
                data.config.setPriority(filedata, str(int(value)))
            self._priority = str(int(value))

    def increasePriority(self):
        new_priority = int(self.priority) + 1 if self.priority and self.priority.isdecimal() else 0
        self.priority = new_priority

    def decreasePriority(self):
        new_priority = int(self.priority) - 1 if self.priority and self.priority.isdecimal() else -1
        if new_priority < 0:
            self.priority = None
        else:
            self.priority = new_priority

    @staticmethod
    def formatName(name: str) -> str:
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

        name = re.sub(r"([a-z]{2,})([A-Z1-9])", r"\1 \2", name)
        name = re.sub(r"(_)", r" ", name)
        name = re.sub(r"([a-zA-Z])-([0-9])", r"\1 \2", name)
        name = re.sub(r"([0-9])-([a-zA-Z])", r"\1 \2", name)

        return name


    def enable(self):
        if (not self.enabled):
            self.addXmlKeys()
            for menu in iter(self.menus):
                if path.exists(data.config.menu + "/" + menu + ".disabled"):
                    rename(
                        data.config.menu + "/" + menu + ".disabled",
                        data.config.menu + "/" + menu)
            for dlc in iter(self.dlcs):
                if path.exists(data.config.dlc + "/" + dlc):
                    for subdir, _, fls in walk(data.config.dlc + "/" + dlc):
                        for file in fls:
                            if (path.exists(subdir + "/" + file)):
                                rename(subdir + "/" + file, subdir + "/" + file[:-9])
            for filedata in iter(self.files):
                if path.exists(data.config.mods + "/~" + filedata):
                    rename(
                        data.config.mods + "/~" + filedata,
                        data.config.mods + "/" + filedata)
            self.enabled = True

    def disable(self):
        if (self.enabled):
            self.removeXmlKeys()
            for menu in iter(self.menus):
                if path.exists(data.config.menu + "/" + menu):
                    rename(
                        data.config.menu + "/" + menu,
                        data.config.menu + "/" + menu + ".disabled")
            for dlc in iter(self.dlcs):
                if path.exists(data.config.dlc + "/" + dlc):
                    for subdir, _, fls in walk(data.config.dlc + "/" + dlc):
                        for file in fls:
                            rename(
                                path.join(subdir, file),
                                path.join(subdir, file) + ".disabled")
            for filedata in iter(self.files):
                if path.exists(data.config.mods + "/" + filedata):
                    rename(
                        data.config.mods + "/" + filedata,
                        data.config.mods + "/~" + filedata)
            self.enabled = False

    def checkPriority(self):
        if (not self.priority):
            for filedata in iter(self.files):
                if (data.config.priority.has_section(filedata)):
                    self.priority = data.config.getPriority(filedata)

    def addXmlKeys(self):
        if (self.xmlkeys):
            text = ''
            with open(data.config.menu + "/input.xml", 'r') as userfile:
                text = userfile.read()
            for xml in iter(self.xmlkeys):
                if (not xml in text):
                    text = text.replace(
                        '<!-- [BASE_CharacterMovement] -->',
                        xml+'\n<!-- [BASE_CharacterMovement] -->')
            with open(data.config.menu + "/input.xml", 'w') as userfile:
                text = userfile.write(text)
        if (self.hidden):
            text = ''
            with open(data.config.menu + "/hidden.xml", 'r') as userfile:
                text = userfile.read()
            for xml in iter(self.hidden):
                if (not xml in text):
                    text = text.replace(
                        '</VisibleVars>',
                        xml+'\n</VisibleVars>')
            with open(data.config.menu + "/hidden.xml", 'w') as userfile:
                text = userfile.write(text)

    def addInputKeys(self):
        added = 0
        if (self.inputsettings):
            text = ''
            with open(data.config.settings + "/input.settings", 'r') as userfile:
                text = userfile.read()
            ask = True
            keep = True
            for key in iter(self.inputsettings):
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
                                    msg = MessageRebindedKeys(key, temp)
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
            with open(data.config.settings + "/input.settings", 'w') as userfile:
                text = userfile.write(text)

    def addUserSettings(self):
        if (self.usersettings):
            text = ''
            with open(data.config.settings + "/user.settings", 'r') as userfile:
                text = userfile.read()
            with open(data.config.settings+"/user.settings", 'w') as userfile:
                text = iter(self.usersettings)[0] + "\n" + text
                userfile.write(text)

    def removeXmlKeys(self):
        if (self.xmlkeys):
            text = ''
            with open(data.config.menu + "/input.xml", 'r') as userfile:
                text = userfile.read()
            for xml in iter(self.xmlkeys):
                if xml in text:
                    text = text.replace(xml+"\n", '')
            with open(data.config.menu + "/input.xml", 'w') as userfile:
                text = userfile.write(text)
        if (self.hidden):
            text = ''
            with open(data.config.menu + "/hidden.xml", 'r') as userfile:
                text = userfile.read()
            for xml in iter(self.hidden):
                if xml in text:
                    text = text.replace(xml+"\n", '')
            with open(data.config.menu + "/hidden.xml", 'w') as userfile:
                text = userfile.write(text)

    def __repr__(self):
        string = "NAME: " + str(self.name) + "\nENABLED: " + str(self.enabled) + \
            "\nPRIORITY: " + self.priority + "\n"
        if (self.files):
            string += "\nDATA:\n"
            for file in iter(self.files):
                string += file + "\n"
        if (self.dlcs):
            string += "\nDLC:\n"
            for dlc in iter(self.dlcs):
                string += dlc + "\n"
        if (self.menus):
            string += "\nMENUS:\n"
            for menu in iter(self.menus):
                string += menu + "\n"
        if (self.xmlkeys):
            string += "\nXML VARIABLES:\n"
            for xml in iter(self.xmlkeys):
                string += xml + "\n"
        if (self.hidden):
            string += "\nHIDDEN XML:\n"
            for xml in iter(self.hidden):
                string += xml + "\n"
        if (self.inputsettings):
            string += "\nINPUT KEYS:\n"
            context = ''
            for key in iter(self.inputsettings):
                if (key.context != context):
                    if (context != ''):
                        string += '\n'
                    context = key.context
                    string += context + '\n'
                string += str(key) + "\n"

        if (self.usersettings):
            string += "\nUSER SETTINGS:\n"
            string += iter(self.usersettings)[0] + "\n"
        return string
