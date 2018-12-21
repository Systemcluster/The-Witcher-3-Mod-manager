'''Configuration module'''
#pylint: disable=invalid-name

import configparser
import os
import os.path as path

class Configuration:
    '''Configuration'''
    documents: str
    config: None
    priority: None

    def __init__(self, documents):
        self.documents = documents
        self.config = configparser.ConfigParser(allow_no_value=True, delimiters='=')
        self.priority = configparser.ConfigParser(allow_no_value=True, delimiters='=')

        if not path.exists(self.documents + "/The Witcher 3 Mod Manager"):
            os.mkdir(self.documents + "/The Witcher 3 Mod Manager")

        self.config.read(self.documents + "/The Witcher 3 Mod Manager/config.ini")
        self.priority.read(self.documents + "/The Witcher 3/mods.settings")

        if not self.config.has_section('PATHS'):
            self.config.add_section('PATHS')
        gamepath = self.config.get('PATHS', 'game')

        if not gamepath:
            raise Exception("Incorrect Game path")

        if not path.exists(gamepath + "/Mods"):
            os.mkdir(gamepath + "/Mods")
        if not self.get('PATHS', 'scriptmerger'):
            self.set('PATHS', 'scriptmerger', '')

        if not self.allowpopups:
            self.allowpopups = '1'
        if not self.language:
            self.language = 'English.qm'
        if not self.config.has_section('TOOLBAR'):
            self.config.add_section('TOOLBAR')

        # self.config.optionxform = str # only for priority

    def write(self, space_around_delimiters=True):
        with open(self.documents + "/The Witcher 3 Mod Manager/config.ini", 'w') as file:
            self.config.write(file, space_around_delimiters)
        with open(self.documents + "/The Witcher 3/mods.settings", 'w') as file:
            self.priority.write(file, space_around_delimiters)

    def read(self):
        with open(self.documents + "/The Witcher 3 Mod Manager/config.ini", 'r') as file:
            return file.read()

    def get(self, section, option):
        if self.config.has_option(section, option):
            return self.config.get(section, option)
        else:
            return ""

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def getPriority(self, section):
        if section in self.priority.sections():
            return self.priority.get(section, 'priority')
        else:
            return None

    def setPriority(self, section, option):
        if not self.priority.has_section(section):
            self.priority.add_section(section)
            self.priority.set(section, 'enabled', '1')
        self.priority.set(section, 'priority', option)

    def setOption(self, section, option):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option)
        self.write()

    def getOptions(self, section):
        if self.config.has_section(section):
            return list(map(lambda x: x[0], self.config.items(section)))
        else:
            return []

    def removeOption(self, section, value):
        if self.config.has_section(section):
            self.config.remove_option(section, value)
        self.write()

    @property
    def scriptmerger(self):
        return self.config.get('PATHS', 'scriptmerger')

    @scriptmerger.setter
    def scriptmerger(self, value):
        self.config.set('PATHS', 'scriptmerger', value)

    @property
    def game(self):
        return self.config.get('PATHS', 'game')

    @game.setter
    def game(self, value):
        self.config.set('PATHS', 'game', value)

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
        return self.documents + "/The Witcher 3 Mod Manager/extracted"

    @property
    def allowpopups(self):
        return self.config.get('SETTINGS', 'AllowPopups')

    @allowpopups.setter
    def allowpopups(self, value):
        self.config.set('SETTINGS', 'AllowPopups', value)

    @property
    def language(self):
        return self.config.get('SETTINGS', 'language')

    @language.setter
    def language(self, value):
        self.config.set('SETTINGS', 'language', value)

    def saveWindowSettings(self, ui, window):
        self.config.set('WINDOW', 'width', str(window.width()))
        self.config.set('WINDOW', 'height', str(window.height()))
        for i in range(start=0, stop=12):
            self.config.set('WINDOW', 'section'+str(i), str(ui.treeWidget.header().sectionSize(i)))

    def setDefaultWindow(self):
        self.config.set('WINDOW', 'width', "1024")
        self.config.set('WINDOW', 'height', "720")
        self.config.set('WINDOW', 'section0', '60')
        self.config.set('WINDOW', 'section1', '200')
        self.config.set('WINDOW', 'section2', '50')
        self.config.set('WINDOW', 'section3', '39')
        self.config.set('WINDOW', 'section4', '39')
        self.config.set('WINDOW', 'section5', '39')
        self.config.set('WINDOW', 'section6', '39')
        self.config.set('WINDOW', 'section7', '45')
        self.config.set('WINDOW', 'section8', '39')
        self.config.set('WINDOW', 'section9', '50')
        self.config.set('WINDOW', 'section10', '45')
        self.config.set('WINDOW', 'section11', '120')

    def correctGamePath(self, gamepath=None):
        if not gamepath:
            gamepath = self.game
        return path.exists(gamepath) and path.exists(path.dirname(gamepath) + "/../../content")
