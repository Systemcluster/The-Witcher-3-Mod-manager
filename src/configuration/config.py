'''Configuration module'''

import configparser
import glob
import json
import os
import os.path as path
import sys
import time
from copy import deepcopy
from typing import TYPE_CHECKING, Union

from fasteners import ReaderWriterLock
from PySide6.QtWidgets import QMainWindow, QMessageBox

from src.globals.constants import translate
from src.gui.alerts import MessageAlertReadingConfigINI
from src.util import util

if TYPE_CHECKING:
    from src.gui.main_widget import CustomMainWidget


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

    __lastPriorityWriteTime: float = 0.0

    def __init__(self, documentsPath: str = '', gamePath: str = '', configPath: str = ''):

        if configPath:
            self.__configPath = configPath
        else:
            if path.isfile(path.realpath(path.curdir) + '/config.ini'):
                self.__configPath = path.realpath(path.curdir)
            else:
                self.__configPath = util.getConfigFolder()

        self.config = configparser.ConfigParser(allow_no_value=True, delimiters="=", strict=False)
        self.priority = configparser.ConfigParser(allow_no_value=True, delimiters="=", strict=False)

        if not path.exists(self.__configPath):
            os.makedirs(self.__configPath)

        self.__writing_config = ReaderWriterLock()
        self.__writing_priority = ReaderWriterLock()

        self.readConfig()

        configured_documents = self.get("PATHS", "documents")
        if documentsPath and not os.path.exists(documentsPath):
            print(f"documents path override {documentsPath} is invalid, starting with existing configuration")

        if documentsPath and os.path.exists(documentsPath):
            self.documents = documentsPath
        elif configured_documents and os.path.exists(configured_documents):
            self.documents = configured_documents
        else:
            self.documents = util.getDocumentsFolder()

        if not self.documents or not os.path.exists(self.documents):
            QMessageBox.critical(
                None,
                translate("Config", "No documents configured"),
                translate("Config", "No documents path configured"),
                QMessageBox.StandardButton.Ok,
            )
            sys.exit(1)

        self.__userSettingsPath = self.documents + '/The Witcher 3'
        if not path.exists(self.__userSettingsPath):
            os.makedirs(self.__userSettingsPath)

        self.set('PATHS', 'documents', self.documents, False)

        self.readPriority()

        if gamePath:
            correctGamePath = self.getCorrectGamePath(gamePath)
            if correctGamePath:
                self.gameexe = correctGamePath
            else:
                print(f"game path override {gamePath} is invalid, starting with existing configuration")

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
        print(f"reading mods.settings from {self.__userSettingsPath + '/mods.settings'}")
        file = self.__userSettingsPath + '/mods.settings'
        with self.__writing_priority.read_lock():
            self.priority.clear()
            if os.path.isfile(file):
                try:
                    self.priority.read(file, encoding=util.detectEncoding(file))
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
                with util.atomicWrite(
                    self.__configPath + '/config.ini', 'w', encoding='utf-8', follow_symlinks=True
                ) as file:
                    print(f"writing config.ini to {self.__configPath + '/config.ini'}")
                    self.config.write(file, space_around_delimiters)
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
                    priority.set(section, f"{option[:1].upper()}{option[1:].lower()}", value)
            with self.__writing_priority.write_lock():
                with util.atomicWrite(
                    self.__userSettingsPath + '/mods.settings', 'w', encoding='utf-8', follow_symlinks=True
                ) as file:
                    print(f"writing mods.settings to {self.__userSettingsPath + '/mods.settings'}")
                    self.__lastPriorityWriteTime = time.monotonic()
                    priority.write(file, space_around_delimiters)
            self.priorityLastWritten = deepcopy(self.priority)

    def write_priority_elapsed(self) -> float:
        '''Returns elapsed time since last priority write.'''
        elapsed_ms = (time.monotonic() - self.__lastPriorityWriteTime) * 1000
        return elapsed_ms

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

    def getWindowSection(self, section: int | str, prefix: str = ""):
        value = self.get('WINDOW', prefix + 'section' + str(section))
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
        configured = self.get('PATHS', 'gameexe')
        if configured:
            configured = util.normalizePath(path.abspath(util.normalizePath(configured)))
        if configured and not path.isfile(configured):
            normalized = util.normalizePath(configured)
            renderer = path.dirname(normalized)
            binaries = path.dirname(renderer)
            if (
                path.basename(normalized).lower() == "witcher3.exe"
                and path.basename(renderer).lower() in ('x64', 'x64_dx12')
                and path.basename(binaries).lower() == "bin"
            ):
                replacement = self.getCorrectGamePath(path.dirname(binaries))
                if replacement:
                    return replacement
        return configured

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
        gameDirectory = self.gameexe
        if not gameDirectory:
            return ''
        return self.getGameRoot(gameDirectory)

    @property
    def launcherconfig(self):
        if self.game:
            try:
                with open(path.join(self.game, 'launcher-configuration.json'), encoding='utf-8-sig') as file:
                    config = json.load(file)
                if isinstance(config, dict) and config.get('gameId') == 'witcher3':
                    return config
            except (OSError, ValueError):
                pass
        return {}

    @property
    def gameversion(self):
        editions = self.launcherconfig.get('editions', [])
        if isinstance(editions, list) and any(
            isinstance(edition, dict) and edition.get("name") == "remasteredEdition" for edition in editions
        ):
            return 're'
        game = self.game
        if (
            game
            and path.isfile(path.join(game, 'bin', 'x64_dx12', 'witcher3.exe'))
            and path.isfile(path.join(game, "bin", "x64", "witcher3.exe"))
        ):
            return 'ng'
        if game and path.isfile(path.join(game, 'bin', 'x64_dx12', 'witcher3.exe')):
            return 're'
        return 'og'

    @property
    def steam(self):
        store = self.launcherconfig.get('platform')
        if store:
            return store == 'steam'
        root = self.game
        return bool(
            root
            and path.basename(path.dirname(root)).lower() == "common"
            and path.isfile(path.join(root, "..", "..", "appmanifest_292030.acf"))
        )

    @property
    def graphicsapi(self):
        gameexe = util.normalizePath(self.gameexe or '')
        if path.basename(path.dirname(gameexe)).lower() == 'x64_dx12':
            return "dx12"
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

    def saveWindowSettings(self, ui: "CustomMainWidget", window: QMainWindow):
        # only save the non-maximized size
        if not window.isMaximized() and not window.isFullScreen():
            self.set('WINDOW', 'width', str(window.width()))
            self.set('WINDOW', 'height', str(window.height()))
        self.set('WINDOW', 'maximized', '1' if window.isMaximized() else '0')
        try:
            self.set("WINDOW", "state", bytes(window.saveState().toBase64().data()).decode("ascii"))
        except Exception as err:
            print('failed to save window state', err, file=sys.stderr)
        for i in range(0, ui.treeWidget.header().count() + 1):
            self.set("WINDOW", "section" + str(i), str(ui.treeWidget.header().sectionSize(i)))
        for i in range(0, ui.loadOrder.header().count() + 1):
            self.set("WINDOW", "losection" + str(i), str(ui.loadOrder.header().sectionSize(i)))
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
    def getGameRoot(gamePath: str) -> str:
        '''Returns the root for a game directory or bin/x64[_dx12] executable.'''
        if not gamePath:
            return ''
        current = util.normalizePath(gamePath)
        selected = current
        if path.isfile(current):
            if path.basename(current).lower() != 'witcher3.exe':
                return ''
            current = path.dirname(current)
            if path.basename(current).lower() not in ('x64', 'x64_dx12'):
                return ''
        if not path.isdir(current):
            return ''
        if path.basename(current).lower() in ('x64', 'x64_dx12'):
            current = path.dirname(current)
            if path.basename(current).lower() != 'bin':
                return ''
        if path.basename(current).lower() == 'bin':
            current = path.dirname(current)
        resolvedRoot = path.normcase(util.normalizePath(path.realpath(current)))
        resolvedSelected = path.normcase(util.normalizePath(path.realpath(selected)))
        content = path.join(current, 'content')
        resolvedContent = path.normcase(util.normalizePath(path.realpath(content)))
        try:
            if path.isdir(content) and all(
                util.normalizePath(path.commonpath((resolvedRoot, candidate))) == util.normalizePath(resolvedRoot)
                for candidate in (resolvedSelected, resolvedContent)
            ):
                return current
        except ValueError:
            pass
        return ''

    @staticmethod
    def getCorrectGamePath(gameExePath: Union[str, None]) -> str:
        '''Validates a selected executable or finds one in a game directory.'''
        if not gameExePath:
            return ''
        normalized = util.normalizePath(path.abspath(util.normalizePath(gameExePath)))
        gameDirectory = Configuration.getGameRoot(normalized)
        if not gameDirectory:
            return ''

        if path.isfile(normalized):
            return normalized
        candidates = (
            path.join(normalized, "witcher3.exe"),
            path.join(gameDirectory, 'bin', 'x64_dx12', 'witcher3.exe'),
            path.join(gameDirectory, "bin", "x64", "witcher3.exe"),
        )
        for candidate in candidates:
            if path.isfile(candidate) and Configuration.getGameRoot(candidate):
                return util.normalizePath(candidate)
        return ''

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
            potentials = [
                path.join(parent, d)
                for d in glob.glob("*", root_dir=parent)
                if path.isdir(path.join(parent, d)) and d.lower() == path.basename(internalPath).lower()
            ]
            existing = next(iter(potentials), None)
            if not existing:
                if create:
                    os.makedirs(internalPath, exist_ok=True)
                    return path.abspath(internalPath)
                else:
                    return None
            return path.abspath(path.join(parent, existing))
        except OSError as e:
            print(f"Error checking path {internalPath}: {e}")
            return None
