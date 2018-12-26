'''Mod management model'''
# pylint: disable=invalid-name,missing-docstring,wildcard-import,unused-wildcard-import

from typing import Dict, List
from os import path
import xml.etree.ElementTree as XML

from src.domain.mod import Mod
from src.globals import data
from src.util.util import *

class Model:
    '''Mod management model'''

    modList: Dict[str, Mod] = {}

    def __init__(self):
        self.reload()

    def reload(self) -> None:
        self.modList = {}
        if path.exists(data.config.configuration + '/installed.xml'):
            tree = XML.parse(data.config.configuration + '/installed.xml')
            root = tree.getroot()
            for xmlmod in root.findall('mod'):
                mod = Mod()
                mod.populateFromXml(xmlmod)
                self.modList[mod.name] = mod

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
            moddir = data.config.mods + ("/~" if not mod.enabled else "/") + file
            openFolder(moddir)
