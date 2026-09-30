'''Mod management model'''

import os
import re
import xml.etree.ElementTree as XML
from base64 import b64decode, b64encode
from collections.abc import KeysView, ValuesView
from io import StringIO
from shutil import copyfileobj

from fasteners import InterProcessLock

from src.core.fetcher import *
from src.domain.key import Key
from src.domain.mod import Mod
from src.globals import data
from src.gui.alerts import (
    MessageAlertReadingConfigurationFailed,
    MessageAlertWritingFailed,
)
from src.util.syntax import *
from src.util.util import *


class Model:
    '''Mod management model'''

    def __init__(self, ignorelock=False):
        if not ignorelock:
            self.lock = InterProcessLock(self.lockfile)
            if not self.lock.acquire(False):
                raise OSError('could not lock ' + self.lockfile)
        self.modList: dict[str, Mod] = {}
        self.reload()

    def reload(self) -> None:
        self._canWrite = False
        self._inventorySource: str | None = None
        errors = []
        for filename in (self.xmlfile, self.xmlfile + ".old", self.xmlfile + ".new"):
            try:
                mods = self._readInventory(filename)
            except FileNotFoundError:
                continue
            except (OSError, ValueError, LookupError, XML.ParseError) as error:
                errors.append(f"{filename}: {error}")
                continue
            self.modList = mods
            self._inventorySource = filename
            self._canWrite = True
            if filename != self.xmlfile:
                print(f"Recovered mod inventory from {filename}")
            return
        if errors:
            failure = XML.ParseError("No valid mod inventory found:\n" + "\n".join(errors))
            MessageAlertReadingConfigurationFailed(self.xmlfile, failure)
            raise failure
        self.modList = {}
        self._canWrite = True

    @staticmethod
    def _readInventory(filename: str) -> dict[str, Mod]:
        encoding = detectEncoding(filename)
        with open(filename, "r", encoding=encoding) as file:
            text = re.sub(
                r"\A(\s*<\?xml[^?\n]*encoding=['\"])utf_8(['\"])(?=[^?\n]*\?>)",
                r"\1utf-8\2",
                file.read(),
                count=1,
            )
        root = XML.parse(StringIO(text)).getroot()
        if root.tag != "installed":
            raise XML.ParseError("Mod inventory must have an installed root element")
        mods: dict[str, Mod] = {}
        for xmlmod in root.findall("mod"):
            if not xmlmod.get("name"):
                raise XML.ParseError("Mod inventory entry is missing its name")
            mod = Model.populateModFromXml(Mod(), xmlmod)
            if not mod.name or mod.name in mods:
                raise XML.ParseError("Mod inventory contains an empty or duplicate mod name")
            mods[mod.name] = mod
        return mods

    def write(self) -> None:
        newfile = self.xmlfile + ".new"
        oldfile = self.xmlfile + ".old"
        try:
            if not self._canWrite:
                raise RuntimeError("Cannot save mod inventory after a failed reload")
            installed = XML.Element("installed")
            root = XML.ElementTree(installed)
            for mod in self.all():
                root = self.writeModToXml(mod, root)
            indent(installed)
            if self._inventorySource is not None:
                self._readInventory(self._inventorySource)
                if self._inventorySource != oldfile:
                    with open(self._inventorySource, "rb") as source, open(oldfile + ".new", "wb") as backup:
                        copyfileobj(source, backup)
                        backup.flush()
                        os.fsync(backup.fileno())
                    os.replace(oldfile + ".new", oldfile)
            print(f"writing mod list to {self.xmlfile}")
            with open(newfile, "wb") as file:
                root.write(file, encoding="utf-8", xml_declaration=True)
                file.flush()
                os.fsync(file.fileno())
            self._readInventory(newfile)
            os.replace(newfile, self.xmlfile)
            self._inventorySource = self.xmlfile
        except Exception as e:
            MessageAlertWritingFailed(self.xmlfile, e)

    def get(self, modname: str) -> Mod:
        return self.modList[modname]

    def list(self) -> KeysView[str]:
        return self.modList.keys()

    def all(self) -> ValuesView[Mod]:
        return self.modList.values()

    def add(self, modname: str, mod: Mod):
        self.modList[modname] = mod
        self.write()

    def remove(self, modname: str):
        if modname in self.modList:
            del self.modList[modname]
        self.write()

    def rename(self, modname: str, newname: str) -> bool:
        if modname not in self.modList or not newname:
            return False
        mod = self.modList[modname]
        del self.modList[modname]
        mod.name = newname
        self.modList[newname] = mod
        self.write()
        return True

    def explore(self, mod: Mod, target_name: str, is_dlc: bool = False) -> None:
        base_dir = data.getConfig().dlc if is_dlc else data.getConfig().mods
        prefix = '/~' if not mod.enabled else '/'
        target_dir = f"{base_dir}{prefix}{target_name}"
        openFolder(target_dir)

    @property
    def xmlfile(self) -> str:
        return os.path.join(data.getConfig().configuration, "installed.xml")

    @property
    def lockfile(self) -> str:
        return os.path.join(data.getConfig().configuration, "installed.lock")

    @staticmethod
    def populateModFromXml(mod: Mod, root: XML.Element) -> Mod:
        mod.date = str(root.get('date'))
        enabled = str(root.get('enabled'))
        if enabled == 'True':
            mod.enabled = True
        else:
            mod.enabled = False
        mod.name = str(root.get('name'))
        prt = str(root.get('priority'))
        if prt != 'Not Set':
            mod.priority = prt
        for elem in root.findall('data'):
            mod.files.append(str(elem.text))
        for elem in root.findall('dlc'):
            mod.dlcs.append(str(elem.text))
        for elem in root.findall('menu'):
            mod.menus.append(str(elem.text))
        for elem in root.findall('xmlkey'):
            mod.xmlkeys.append(str(elem.text))
        for elem in root.findall('hidden'):
            mod.hidden.append(str(elem.text))
        for elem in root.findall('key'):
            context = elem.get("context")
            if context is None:
                raise XML.ParseError("Input key is missing its context")
            key = Key(context, str(elem.text))
            mod.inputsettings.append(key)
        for elem in root.findall('settings'):
            # legacy usersetting storage format
            settings = fetchUserSettings(str(elem.text))
            for setting in iter(settings):
                mod.usersettings.append(setting)
        for elem in root.findall('setting'):
            usersetting = Usersetting(str(elem.get('context')), str(elem.text))
            mod.usersettings.append(usersetting)
        for elem in root.findall('readme'):
            # legacy readme format
            mod.readmes.append(str(elem.text))
        for elem in root.findall('readmeb64'):
            try:
                mod.readmes.append(b64decode(str(elem.text).encode("ascii")).decode("utf-8"))
            except:
                print('could not decode readme')

        mod.checkPriority()
        return mod

    @staticmethod
    def writeModToXml(mod: Mod, root: XML.ElementTree) -> XML.ElementTree:
        installed = root.getroot()
        if installed is None:
            raise ValueError("Mod XML tree has no root element")
        elem = XML.SubElement(installed, "mod")
        elem.set('name', mod.name)
        elem.set('enabled', str(mod.enabled))
        elem.set('date', mod.date)
        elem.set('priority', mod.priority)
        if mod.files:
            for file in mod.files:
                XML.SubElement(elem, 'data').text = file
        if mod.dlcs:
            for dlc in mod.dlcs:
                XML.SubElement(elem, 'dlc').text = dlc
        if mod.menus:
            for menu in mod.menus:
                XML.SubElement(elem, 'menu').text = menu
        if mod.xmlkeys:
            for xml in mod.xmlkeys:
                XML.SubElement(elem, 'xmlkey').text = xml
        if mod.hidden:
            for xml in mod.hidden:
                XML.SubElement(elem, 'hidden').text = xml
        if mod.inputsettings:
            for key in mod.inputsettings:
                ky = XML.SubElement(elem, 'key')
                ky.text = str(key)
                ky.set('context', key.context)
        if mod.usersettings:
            for usersetting in mod.usersettings:
                us = XML.SubElement(elem, 'setting')
                us.text = str(usersetting)
                us.set('context', usersetting.context)
        if mod.readmes:
            for readme in mod.readmes:
                us = XML.SubElement(elem, 'readmeb64')
                us.text = b64encode(str(readme).encode("utf-8")).decode("ascii")
        return root
