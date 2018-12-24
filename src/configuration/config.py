'''Configuration module'''
# pylint: disable=invalid-name,missing-docstring

import configparser
import os
import os.path as path

from PyQt5.QtWidgets import QMainWindow, QWidget

class Configuration:
    '''Configuration'''
    documents: str = ""
    gamePath: str = ""
    configPath: str = ""
    userSettingsPath: str = ""
    config: configparser.ConfigParser = None
    priority: configparser.ConfigParser = None

    def __init__(self, documentsPath: str, gamePath: str = ""):
        self.documents = documentsPath
        self.userSettingsPath = self.documents + "/The Witcher 3"

        if path.isfile(path.curdir + "/config.ini"):
            self.configPath = path.curdir
        else:
            self.configPath = self.documents + "/The Witcher 3 Mod Manager"

        self.config = configparser.ConfigParser(allow_no_value=True, delimiters='=')
        self.priority = configparser.ConfigParser(allow_no_value=True, delimiters='=')

        if not path.exists(self.configPath):
            os.mkdir(self.configPath)

        self.config.read(self.configPath + "/config.ini")
        self.priority.read(self.userSettingsPath + "/mods.settings")

        if not self.config.has_section('PATHS'):
            self.config.add_section('PATHS')
        gamePath = self.correctGamePath(gamePath)
        if not gamePath:
            raise Exception("Incorrect Game path")
        self.set('PATHS', 'game', gamePath)

        for _ in range(3):
            gamePath, _ = path.split(gamePath)
        if not path.exists(gamePath + "/Mods"):
            os.mkdir(gamePath + "/Mods")
        if not self.get('PATHS', 'scriptmerger'):
            self.set('PATHS', 'scriptmerger', '')

        self.set('PATHS', 'mod', gamePath + "/Mods")
        self.set('PATHS', 'dlc', gamePath + "/DLC")
        self.set('PATHS', 'menu', gamePath + "/bin/config/r4game/user_config_matrix/pc")
        self.set('PATHS', 'settings', self.documents + "/The Witcher 3")

        if not self.allowpopups:
            self.allowpopups = '1'
        if not self.language:
            self.language = 'English.qm'
        if not self.config.has_section('TOOLBAR'):
            self.config.add_section('TOOLBAR')


    def write(self, space_around_delimiters=True):
        with open(self.configPath + "/config.ini", 'w') as file:
            self.config.write(file, space_around_delimiters)
        with open(self.userSettingsPath + "/mods.settings", 'w') as file:
            self.priority.write(file, space_around_delimiters)

    def read(self):
        with open(self.configPath + "/config.ini", 'r') as file:
            return file.read()

    def get(self, section, option):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        return None

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)


    def getPriority(self, section):
        if section in self.priority.sections():
            return self.priority.get(section, 'priority')
        return None

    def setPriority(self, section, option):
        if not self.priority.has_section(section):
            self.priority.add_section(section)
            self.priority.set(section, 'enabled', '1')
        self.priority.set(section, 'priority', option)

    def removePriority(self, section):
        if self.priority.has_section(section):
            self.priority.remove_section(section)
        self.write()

    def getOptions(self, section):
        if self.config.has_section(section):
            return list(map(lambda x: x[0], self.config.items(section)))
        return []

    def setOption(self, section, option):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option)
        self.write()

    def removeOption(self, section, value):
        if self.config.has_section(section):
            self.config.remove_option(section, value)
        self.write()


    @property
    def scriptmerger(self):
        return self.get('PATHS', 'scriptmerger')

    @scriptmerger.setter
    def scriptmerger(self, value):
        self.set('PATHS', 'scriptmerger', value)

    @property
    def game(self):
        return self.get('PATHS', 'game')

    @game.setter
    def game(self, value):
        self.set('PATHS', 'game', value)

    @property
    def mods(self):
        return self.game + "/mods"

    @property
    def dlc(self):
        return self.game + "/dlc"

    @property
    def menu(self):
        return self.game + "/bin/config/r4game/user_config_matrix/pc"

    @property
    def settings(self):
        return self.documents + "/The Witcher 3"

    @property
    def configuration(self):
        return self.documents + "/The Witcher 3 Mod Manager"

    @property
    def extracted(self):
        return self.configPath + "/extracted"

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


    def saveWindowSettings(self, ui: QWidget, window: QMainWindow):
        self.set('WINDOW', 'width', str(window.width()))
        self.set('WINDOW', 'height', str(window.height()))
        for i in range(0, ui.treeWidget.header().count()+1):
            self.set('WINDOW', 'section'+str(i), str(ui.treeWidget.header().sectionSize(i)))

    def setDefaultWindow(self):
        self.set('WINDOW', 'width', "1024")
        self.set('WINDOW', 'height', "720")
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

    def correctGamePath(self, gamePath=None) -> str:
        if not gamePath:
            gamePath = self.game
        return gamePath if gamePath and path.exists(gamePath) and \
            path.exists(path.dirname(gamePath) + "/../../content") else ""
