'''Configuration module'''
# pylint: disable=invalid-name,missing-docstring

import configparser
import os
import os.path as path
from copy import deepcopy
from typing import Union

from PyQt5.QtWidgets import QMainWindow, QWidget

from src.util.util import normalizePath

class Configuration:
    '''Configuration'''

    __configPath: str = ''
    __userSettingsPath: str = ''

    config: configparser.ConfigParser = None
    priority: configparser.ConfigParser = None

    def __init__(self, documentsPath: str, gamePath: str = ''):
        self.documents = documentsPath
        self.__userSettingsPath = self.documents + '/The Witcher 3'

        if path.isfile(path.curdir + '/config.ini'):
            self.__configPath = path.curdir
        else:
            self.__configPath = self.documents + '/The Witcher 3 Mod Manager'

        self.config = configparser.ConfigParser(allow_no_value=True, delimiters='=')
        self.priority = configparser.ConfigParser(allow_no_value=True, delimiters='=')

        if not path.exists(self.__configPath):
            os.mkdir(self.__configPath)
        if not path.exists(self.__userSettingsPath):
            os.mkdir(self.__userSettingsPath)

        self.config.read(self.__configPath + '/config.ini')
        self.priority.read(self.__userSettingsPath + '/mods.settings')

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


    def write(self, space_around_delimiters: bool = True):
        with open(self.__configPath + '/config.ini', 'w') as file:
            self.config.write(file, space_around_delimiters)
        with open(self.__userSettingsPath + '/mods.settings', 'w') as file:
            # proper-case all keys
            priority = deepcopy(self.priority)
            priority.optionxform = str
            for section in priority.sections():
                for option in priority.options(section):
                    value = priority.get(section, option)
                    priority.remove_option(section, option)
                    priority.set(section, f'{option[:1].upper()}{option[1:].lower()}', value)
            priority.write(file, space_around_delimiters)

    def read(self):
        with open(self.__configPath + '/config.ini', 'r') as file:
            return file.read()

    def get(self, section: str, option: str):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        return None

    def set(self, section: str, option: str, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)


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

    def getWindowSection(self, section: str):
        value = self.get('WINDOW', 'section'+str(section))
        return int(value) if value else None

    def getOptions(self, section: str):
        if self.config.has_section(section):
            return list(map(lambda x: x[0], self.config.items(section)))
        return []

    def setOption(self, section: str, option: str):
        if not self.config.has_section(section):
            self.priority.add_section(section)
        self.config.set(section, option)
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
            self.set('WINDOW', 'section'+str(i), str(ui.treeWidget.header().sectionSize(i)))

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
