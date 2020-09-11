'''Configuration module'''
# pylint: disable=invalid-name,missing-docstring

import configparser
import sys
import os
import os.path as path
from copy import deepcopy
from typing import Union

from PySide2.QtWidgets import QMainWindow, QMessageBox, QWidget

from src.util.util import detectEncoding, getConfigFolder, getConfigFolderName, getDocumentsFolder, normalizePath
from src.gui.alerts import MessageAlertReadingConfigINI


class Configuration:
    '''Configuration'''

    __configPath: str = ''
    __userSettingsPath: str = ''

    config: configparser.ConfigParser = None  # type: ignore
    priority: configparser.ConfigParser = None  # type: ignore

    configLastWritten: configparser.ConfigParser = None  # type: ignore
    priorityLastWritten: configparser.ConfigParser = None  # type: ignore

    def __init__(self, documentsPath: str = '', gamePath: str = '', configPath: str = ''):

        if configPath:
            self.__configPath = configPath
        else:
            if path.isfile(path.curdir + '/config.ini'):
                self.__configPath = path.curdir
            else:
                self.__configPath = getConfigFolder() + '/' + getConfigFolderName()

        self.config = configparser.ConfigParser(
            allow_no_value=True, delimiters='=')
        self.priority = configparser.ConfigParser(
            allow_no_value=True, delimiters='=')

        if not path.exists(self.__configPath):
            os.mkdir(self.__configPath)

        self.readConfig()

        if documentsPath and os.path.exists(documentsPath):
            self.documents = documentsPath
        elif self.get('PATHS', 'documents') and os.path.exists(self.get('PATHS', 'documents')):
            self.documents = self.get('PATHS', 'documents')
        else:
            self.documents = getDocumentsFolder()

        if not self.documents or not os.path.exists(self.documents):
            QMessageBox.critical(
                None,
                "No documents configured",
                "No documents path configured",
                QMessageBox.StandardButton.Ok)
            sys.exit(1)

        self.__userSettingsPath = self.documents + '/The Witcher 3'
        if not path.exists(self.__userSettingsPath):
            os.mkdir(self.__userSettingsPath)

        self.set('PATHS', 'documents', self.documents)

        self.readPriority()

        gamePath = self.getCorrectGamePath(gamePath)
        if gamePath:
            self.game = gamePath

        if not self.get('PATHS', 'scriptmerger'):
            self.set('PATHS', 'scriptmerger', '')
        if not self.allowpopups:
            self.allowpopups = '1'
        if not self.language:
            self.language = 'English.qm'
        if not self.config.has_section('TOOLBAR'):
            self.config.add_section('TOOLBAR')

    def readPriority(self):
        self.priority.clear()
        file = self.__userSettingsPath + '/mods.settings'
        self.priority.read(file, encoding=detectEncoding(file))

    def readConfig(self):
        print(f"reading config.ini from {self.__configPath + '/config.ini'}")
        file = self.__configPath + '/config.ini'
        if os.path.isfile(file):
            try:
                self.config.read(file, encoding=detectEncoding(file))
            except Exception as e:
                MessageAlertReadingConfigINI(file, e)

    def write(self, space_around_delimiters: bool = False):
        if self.config != self.configLastWritten:
            with open(self.__configPath + '/config.ini', 'w', encoding='utf-8') as file:
                print(
                    f"writing config.ini to {self.__configPath + '/config.ini'}")
                self.config.write(file, space_around_delimiters)
            self.configLastWritten = deepcopy(self.config)
        if self.priority != self.priorityLastWritten:
            with open(self.__userSettingsPath + '/mods.settings', 'w', encoding='utf-8') as file:
                print(
                    f"writing mods.settings to {self.__configPath + '/mods.settings'}")
                # proper-case all keys
                priority = deepcopy(self.priority)
                priority.optionxform = str  # type: ignore
                for section in priority.sections():
                    for option in priority.options(section):
                        value = priority.get(section, option)
                        priority.remove_option(section, option)
                        priority.set(
                            section, f'{option[:1].upper()}{option[1:].lower()}', value)
                priority.write(file, space_around_delimiters)
            self.priorityLastWritten = deepcopy(self.priority)

    def get(self, section: str, option: str):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        return None

    def set(self, section: str, option: str, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        self.write()

    def getPriority(self, section: str):
        if self.priority.has_section(section):
            if self.priority.has_option(section, 'priority'):
                return self.priority.get(section, 'priority')
            return None
        return None

    def setPriority(self, section: str, option: str):
        if not self.priority.has_section(section):
            self.priority.add_section(section)
            self.priority.set(section, 'enabled', '1')
        self.priority.set(section, 'priority', option)

    def removePriority(self, section: str):
        if self.priority.has_section(section):
            self.priority.remove_section(section)
        self.write()

    def getWindowSection(self, section: str, prefix: str = ''):
        value = self.get('WINDOW', prefix+'section'+str(section))
        return int(value) if value else None

    def getOptions(self, section: str):
        if self.config.has_section(section):
            return list(map(lambda x: x[0], self.config.items(section)))
        return []

    def setOption(self, section: str, option: str):
        if not self.config.has_section(section):
            self.priority.add_section(section)
        self.config.set(section, option, "")
        self.write()

    def removeOption(self, section: str, option: str):
        if self.config.has_section(section):
            self.config.remove_option(section, option)
        self.write()

    @property
    def scriptmerger(self):
        return self.get('PATHS', 'scriptmerger')

    @scriptmerger.setter
    def scriptmerger(self, value: str):
        self.set('PATHS', 'scriptmerger', value)

    @property
    def game(self):
        return self.get('PATHS', 'game')

    @game.setter
    def game(self, value: str):
        gamePath = self.getCorrectGamePath(value)
        if not gamePath:
            raise ValueError('Invalid game path \'' + value + '\'')
        self.set('PATHS', 'game', gamePath)
        if not path.exists(gamePath + '/Mods'):
            os.mkdir(gamePath + '/Mods')

    @property
    def allowpopups(self):
        return self.get('SETTINGS', 'AllowPopups')

    @allowpopups.setter
    def allowpopups(self, value):
        self.set('SETTINGS', 'AllowPopups', value)

    @property
    def language(self):
        return self.get('SETTINGS', 'language')

    @language.setter
    def language(self, value):
        self.set('SETTINGS', 'language', value)

    @property
    def lastpath(self):
        return self.get('PATHS', 'lastpath')

    @lastpath.setter
    def lastpath(self, value):
        self.set('PATHS', 'lastpath', value)

    @property
    def mods(self):
        return self.game and self.game + '/Mods'

    @property
    def dlc(self):
        return self.game and self.game + '/DLC'

    @property
    def menu(self):
        return self.game and self.game + '/bin/config/r4game/user_config_matrix/pc'

    @property
    def settings(self):
        return self.__userSettingsPath

    @property
    def configuration(self):
        return self.__configPath

    @property
    def extracted(self):
        return self.__configPath + '/extracted'

    @property
    def gameexe(self):
        return self.game and self.game + '/bin/x64/witcher3.exe'

    def saveWindowSettings(self, ui: QWidget, window: QMainWindow):
        self.set('WINDOW', 'width', str(window.width()))
        self.set('WINDOW', 'height', str(window.height()))
        for i in range(0, ui.treeWidget.header().count()+1):
            self.set('WINDOW', 'section'+str(i),
                     str(ui.treeWidget.header().sectionSize(i)))
        for i in range(0, ui.loadOrder.header().count() + 1):
            self.set('WINDOW', 'losection'+str(i),
                     str(ui.loadOrder.header().sectionSize(i)))
        hsplit = ui.horizontalSplitter_tree.sizes()
        self.set('WINDOW', 'hsplit0', str(hsplit[0]))
        self.set('WINDOW', 'hsplit1', str(hsplit[1]))

    def setDefaultWindow(self):
        self.set('WINDOW', 'width', '1024')
        self.set('WINDOW', 'height', '720')
        self.set('WINDOW', 'section0', '60')
        self.set('WINDOW', 'section1', '200')
        self.set('WINDOW', 'section2', '50')
        self.set('WINDOW', 'section3', '39')
        self.set('WINDOW', 'section4', '39')
        self.set('WINDOW', 'section5', '39')
        self.set('WINDOW', 'section6', '39')
        self.set('WINDOW', 'section7', '45')
        self.set('WINDOW', 'section8', '39')
        self.set('WINDOW', 'section9', '50')
        self.set('WINDOW', 'section10', '45')
        self.set('WINDOW', 'section11', '120')

    @staticmethod
    def getCorrectGamePath(gamePath: Union[str, None]) -> str:
        '''Checks and corrects game path'''
        if not gamePath:
            return ''
        _, ext = path.splitext(gamePath)
        if ext == '.exe':
            for _ in range(3):
                gamePath, _ = path.split(gamePath)
        return normalizePath(gamePath) if path.exists(gamePath) \
            and path.exists(gamePath + '/content') \
            and path.isfile(gamePath + '/bin/x64/witcher3.exe') else ''
