'''Mod management model'''
# pylint: disable=invalid-name,missing-docstring,wildcard-import,unused-wildcard-import

from typing import Dict, List
from os import path
import xml.etree.ElementTree as XML

from fasteners import InterProcessLock

from src.domain.mod import Mod
from src.domain.key import Key
from src.globals import data
from src.util.util import *
from src.util.syntax import *

class Model:
    '''Mod management model'''

    def __init__(self, ignorelock=False):
        if not ignorelock:
            self.lock = InterProcessLock(self.lockfile)
            if not self.lock.acquire(False):
                raise IOError('could not lock ' + self.lockfile)
        self.modList: Dict[str, Mod] = {}
        self.reload()

    def reload(self) -> None:
        self.modList = {}
        if path.exists(self.xmlfile):
            tree = XML.parse(self.xmlfile)
            root = tree.getroot()
            for xmlmod in root.findall('mod'):
                mod = self.populateModFromXml(Mod(), xmlmod)
                self.modList[mod.name] = mod

    def write(self) -> None:
        root = XML.Element('installed')
        for mod in self.all():
            root = self.writeModToXml(mod, root)
        indent(root)
        tree = XML.ElementTree(root)
        tree.write(self.xmlfile)

    def get(self, modname: str) -> Mod:
        return self.modList[modname]

    def list(self) -> List[str]:
        return self.modList.keys()

    def all(self) -> List[Mod]:
        return self.modList.values()

    def add(self, modname: str, mod: Mod):
        self.modList[modname] = mod

    def remove(self, modname: str):
        del self.modList[modname]

    def rename(self, modname: str, newname: str) -> bool:
        if not modname in self.modList:
            return False
        mod = self.modList[modname]
        del self.modList[modname]
        mod.name = newname
        self.modList[newname] = mod
        return True

    def explore(self, modname: str) -> None:
        mod = self.modList[modname]
        for file in mod.files:
            moddir = data.config.mods + ('/~' if not mod.enabled else '/') + file
            openFolder(moddir)

    @property
    def xmlfile(self) -> str:
        return data.config.configuration + '/installed.xml'

    @property
    def lockfile(self) -> str:
        return data.config.configuration + '/installed.lock'

    @staticmethod
    def populateModFromXml(mod: Mod, root: XML.ElementTree) -> Mod:
        mod.date = root.get('date')
        enabled = root.get('enabled')
        if enabled == 'True':
            mod.enabled = True
        else:
            mod.enabled = False
        mod.name = root.get('name')
        prt = root.get('priority')
        if prt != 'Not Set':
            mod.priority = prt
        for elem in root.findall('data'):
            mod.files.append(elem.text)
        for elem in root.findall('dlc'):
            mod.dlcs.append(elem.text)
        for elem in root.findall('menu'):
            mod.menus.append(elem.text)
        for elem in root.findall('xmlkey'):
            mod.xmlkeys.append(elem.text)
        for elem in root.findall('hidden'):
            mod.hidden.append(elem.text)
        for elem in root.findall('key'):
            key = Key(elem.get('context'), elem.text)
            mod.inputsettings.append(key)
        for elem in root.findall('settings'):
            mod.usersettings.append(elem.text)
        mod.checkPriority()
        return mod

    @staticmethod
    def writeModToXml(mod: Mod, root: XML.ElementTree) -> XML.ElementTree:
        elem = XML.SubElement(root, 'mod')
        elem.set('name', mod.name)
        elem.set('enabled', str(mod.enabled))
        elem.set('date', mod.date)
        elem.set('priority', mod.getPriority())
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
            XML.SubElement(elem, 'settings').text = mod.usersettings[0]
        return root
