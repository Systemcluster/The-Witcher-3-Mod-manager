'''Configuration module'''
# pylint: disable=invalid-name,missing-docstring

import configparser
import glob
import os
import os.path as path
import sys
from copy import deepcopy
from typing import Union

from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget
from fasteners import ReaderWriterLock

from src.globals.constants import translate
from src.gui.alerts import MessageAlertReadingConfigINI
from src.util import util


class Configuration:
    '''Configuration'''

    __configPath: str = ''
    __userSettingsPath: str = ''

    __writing_config: ReaderWriterLock
    __writing_priority: ReaderWriterLock

    config: configparser.ConfigParser = None  # type: ignore
    priority: configparser.ConfigParser = None  # type: ignore

    configLastWritten: configparser.ConfigParser = None  # type: ignore
    priorityLastWritten: configparser.ConfigParser = None  # type: ignore

    def __init__(self, documentsPath: str = '', gamePath: str = '', configPath: str = ''):

        if configPath:
            self.__configPath = configPath
        else:
            if path.isfile(path.realpath(path.curdir) + '/config.ini'):
                self.__configPath = path.realpath(path.curdir)
            else:
                self.__configPath = util.getConfigFolder() + '/' + util.getConfigFolderName()

        self.config = configparser.ConfigParser(
            allow_no_value=True, delimiters='=', strict=False)
        self.priority = configparser.ConfigParser(
            allow_no_value=True, delimiters='=', strict=False)

        if not path.exists(self.__configPath):
            os.mkdir(self.__configPath)

        self.__writing_config = ReaderWriterLock()
        self.__writing_priority = ReaderWriterLock()

        self.readConfig()

        if documentsPath and not os.path.exists(documentsPath):
            print(
                f'documents path override {documentsPath} is invalid, starting with existing configuration')

        if documentsPath and os.path.exists(documentsPath):
            self.documents = documentsPath
        elif self.get('PATHS', 'documents') and os.path.exists(self.get('PATHS', 'documents')):
            self.documents = self.get('PATHS', 'documents')
        else:
            self.documents = util.getDocumentsFolder()

        if not self.documents or not os.path.exists(self.documents):
            QMessageBox.critical(
                None,
                translate("Config", "No documents configured"),
                translate("Config", "No documents path configured"),
                QMessageBox.StandardButton.Ok)
            sys.exit(1)

        self.__userSettingsPath = self.documents + '/The Witcher 3'
        if not path.exists(self.__userSettingsPath):
            os.mkdir(self.__userSettingsPath)

        self.set('PATHS', 'documents', self.documents, False)

        self.readPriority()

        if gamePath:
            correctGamePath = self.getCorrectGamePath(gamePath)
            if correctGamePath:
                self.game = correctGamePath
            else:
                print(
                    f'game path override {gamePath} is invalid, starting with existing configuration')

        self._DLC = None
        self._MODS = None

        if not self.get('PATHS', 'scriptmerger'):
            self.set('PATHS', 'scriptmerger', '', False)
        if not self.allowpopups:
            self.allowpopups = '1'
        if not self.language:
            self.language = 'English.qm'
        if not self.config.has_section('TOOLBAR'):
            self.config.add_section('TOOLBAR')

    def readPriority(self):
        print(
            f"reading mods.settings from {self.__userSettingsPath + '/mods.settings'}")
        file = self.__userSettingsPath + '/mods.settings'
        with self.__writing_priority.read_lock():
            self.priority.clear()
            if os.path.isfile(file):
                try:
                    self.priority.read(
                        file, encoding=util.detectEncoding(file))
                except Exception as e:
                    MessageAlertReadingConfigINI(file, e)
            else:
                print("mods.settings not found, creating new file")

    def readConfig(self):
        print(f"reading config.ini from {self.__configPath + '/config.ini'}")
        file = self.__configPath + '/config.ini'
        with self.__writing_config.read_lock():
            self.config.clear()
            if os.path.isfile(file):
                try:
                    self.config.read(file, encoding=util.detectEncoding(file))
                except Exception as e:
                    MessageAlertReadingConfigINI(file, e)
                else:
                    print("config.ini not found, creating new file")

    @util.debounce(25)
    def write_config(self, space_around_delimiters: bool = False):
        if self.config != self.configLastWritten:
            with self.__writing_config.write_lock():
                with open(self.__configPath + '/config.ini', 'w', encoding='utf-8') as file:
                    print(
                        f"writing config.ini to {self.__configPath + '/config.ini'}")
                    self.config.write(file, space_around_delimiters)
                    file.flush()
                    os.fsync(file.fileno())
            self.configLastWritten = deepcopy(self.config)

    @util.debounce(25)
    def write_priority(self, space_around_delimiters: bool = False):
        if self.priority != self.priorityLastWritten:
            # proper-case all keys
            priority = deepcopy(self.priority)
            priority.optionxform = str  # type: ignore
            for section in priority.sections():
                for option in priority.options(section):
                    value = priority.get(section, option)
                    priority.remove_option(section, option)
                    priority.set(
                        section, f'{option[:1].upper()}{option[1:].lower()}', value)
            with self.__writing_priority.write_lock():
                with open(self.__userSettingsPath + '/mods.settings', 'w', encoding='utf-8') as file:
                    print(
                        f"writing mods.settings to {self.__userSettingsPath + '/mods.settings'}")
                    priority.write(file, space_around_delimiters)
                    file.flush()
                    os.fsync(file.fileno())
            self.priorityLastWritten = deepcopy(self.priority)

    def get(self, section, option, default=None):
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def set(self, section: str, option: str, value, write: bool = True):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)
        if write:
            self.write_config()

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
        self.write_priority()

    def getWindowSection(self, section: str, prefix: str = ''):
        value = self.get('WINDOW', prefix+'section'+str(section))
        return int(value) if value else None

    def getOptions(self, section: str):
        if self.config.has_section(section):
            return list(map(lambda x: x[0], self.config.items(section)))
        return []

    def setOption(self, section: str, option: str):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, "")
        self.write_config()

    def removeOption(self, section: str, option: str):
        if self.config.has_section(section):
            self.config.remove_option(section, option)
        self.write_config()

    @property
    def scriptmerger(self):
        return self.get('PATHS', 'scriptmerger')

    @scriptmerger.setter
    def scriptmerger(self, value: str):
        self.set('PATHS', 'scriptmerger', value)

    @property
    def gameexe(self):
        return self.get('PATHS', 'gameexe')

    @gameexe.setter
    def gameexe(self, value: str):
        gameexe = self.getCorrectGamePath(value)
        if not gameexe:
            raise ValueError('Invalid game exe path \'' + value + '\'')
        self.set('PATHS', 'gameexe', gameexe)
        self._MODS = None
        self._DLC = None

    @property
    def game(self):
        gameDirectory = self.get('PATHS', 'gameexe')
        for _ in range(3):
            gameDirectory, _ = path.split(gameDirectory)
        return gameDirectory

    @property
    def gameversion(self):
        if path.exists(self.game + "/bin/x64_dx12"):
            return "ng"
        else:
            return "og"

    @property
    def graphicsapi(self):
        if "x64_dx12" in self.gameexe:
            return "dx12"
        else:
            return "dx11"

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
        if self._MODS is not None:
            return self._MODS
        if not self.game:
            return None
        self._MODS = self.verifyInternalPath(self.game + '/Mods', create=True)
        return self._MODS

    @property
    def dlc(self):
        if self._DLC is not None:
            return self._DLC
        if not self.game:
            return None
        self._DLC = self.verifyInternalPath(self.game + '/DLC', create=True)
        return self._DLC

    @property
    def menu(self):
        return self.game and self.game + '/bin/config/r4game/user_config_matrix/pc'

    @property
    def settings(self):
        return self.__userSettingsPath

    @property
    def usersettings(self):
        return "dx12user.settings" if self.graphicsapi == "dx12" else "user.settings"

    @property
    def configuration(self):
        return self.__configPath

    @property
    def extracted(self):
        return self.__configPath + '/extracted'

    @property
    def gamelaunchcommand(self):
        return self.get("PATHS", "gamelaunchcommand")

    @property
    def mergerlaunchcommand(self):
        return self.get("PATHS", "mergerlaunchcommand")

    @property
    def theme(self):
        return self.get('SETTINGS', 'theme', 'Follow System')
    
    @theme.setter
    def theme(self, value):
        self.set('SETTINGS', 'theme', value)

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
    def getCorrectGamePath(gameExePath: Union[str, None]) -> str:
        '''Checks and corrects game path'''
        if not gameExePath:
            return ''
        _, ext = path.splitext(gameExePath)
        gameDirectory = gameExePath
        if ext == '.exe':
            for _ in range(3):
                gameDirectory, _ = path.split(gameDirectory)
        return util.normalizePath(gameExePath) if path.exists(gameDirectory) \
            and path.exists(gameDirectory + '/content') \
            and path.isfile(gameDirectory + '/bin/x64/witcher3.exe') else ''

    @staticmethod
    def verifyInternalPath(internalPath: str | None, create: bool = False) -> str | None:
        if not internalPath:
            return None
        try:
            if path.isdir(internalPath):
                return path.abspath(internalPath)
            parent = path.abspath(path.join(internalPath, path.pardir))
            if not path.isdir(parent):
                if create:
                    os.makedirs(internalPath, exist_ok=True)
                    return path.abspath(internalPath)
                else:
                    return None
            potentials = [path.join(parent, d) for d in glob.glob(
                '*', root_dir=parent) if path.isdir(path.join(parent, d)) and d.lower() == path.basename(internalPath).lower()]
            existing = next(iter(potentials), None)
            if not existing:
                if create:
                    os.makedirs(internalPath, exist_ok=True)
                    return path.abspath(internalPath)
                else:
                    return None
            return path.abspath(existing)
        except OSError as e:
            print(f'Error checking path {internalPath}: {e}')
            return None
