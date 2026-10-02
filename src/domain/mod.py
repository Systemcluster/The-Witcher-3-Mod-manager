'''Mod Class'''

import re
from dataclasses import dataclass, field
from os import path, walk
from time import gmtime, strftime
from typing import List, Optional, Tuple, Union

from PySide6.QtWidgets import QMessageBox

from src.domain.key import Key
from src.domain.usersetting import Usersetting
from src.globals import data
from src.globals.constants import translate
from src.gui.alerts import MessageRebindKeys
from src.util.util import *


@dataclass
class Mod:
    '''Mod object containing all mod data'''

    _name: str = ''
    _priority: Optional[str] = ''
    enabled: bool = True
    date: str = ''
    source: str = ''

    files: List[str] = field(default_factory=list)
    dlcs: List[str] = field(default_factory=list)
    menus: List[str] = field(default_factory=list)
    xmlkeys: List[str] = field(default_factory=list)
    usersettings: List[Usersetting] = field(default_factory=list)
    inputsettings: List[Key] = field(default_factory=list)
    hidden: List[str] = field(default_factory=list)
    readmes: List[str] = field(default_factory=list)

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
                data.getConfig().removePriority(modfile)
            self._priority = None
        else:
            for filedata in iter(self.files):
                data.getConfig().setPriority(filedata, str(int(value)))
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
        if re.match("^mod.*", name):
            name = name[3:]

        length = len(name)
        for match in re.finditer(r"-[0-9]+-.+", name):
            length = match.span()[0]
        name = name[0:length]

        if re.search(r".*\.(zip|rar)$", name):
            name = name[:-4]
        elif re.search(r".*\.7z$", name):
            name = name[:-3]

        name = re.sub(r"([a-z]{2,})([A-Z1-9])", r"\1 \2", name)
        name = re.sub(r"(_)", r" ", name)
        name = re.sub(r"([a-zA-Z])-([0-9])", r"\1 \2", name)
        name = re.sub(r"([0-9])-([a-zA-Z])", r"\1 \2", name)

        return name

    def enable(self) -> list[str]:
        incomplete = []
        if not self.enabled:
            try:
                self.installXmlKeys()
            except Exception as e:
                incomplete.append("input.xml")
                print("failed to install xmlkeys", e)
            try:
                self.installMenus()
            except Exception as e:
                incomplete.append(translate("MainWindow", "menu xml files"))
                print("failed to install menus", e)
            for menu in iter(self.menus):
                if path.exists(data.getConfig().menu + "/" + menu + ".disabled"):
                    renameInstalledPath(
                        data.getConfig().menu + "/" + menu + ".disabled",
                        data.getConfig().menu + "/" + menu,
                        modDirectory=False,
                    )
            for dlc in iter(self.dlcs):
                dlc_directory = data.getConfig().dlc
                if dlc_directory is None:
                    raise ValueError("No game directory configured for DLC files")
                if path.exists(dlc_directory + "/" + dlc):
                    for subdir, _, fls in walk(dlc_directory + "/" + dlc):
                        for file in fls:
                            if path.exists(subdir + "/" + file):
                                if file.endswith(".disabled") and not file.startswith("."):
                                    renameInstalledPath(
                                        subdir + "/" + file, subdir + "/" + file[:-9], modDirectory=True
                                    )
            for filedata in iter(self.files):
                mods_directory = data.getConfig().mods
                if mods_directory is None:
                    raise ValueError("No game directory configured for mod files")
                if path.exists(mods_directory + "/~" + filedata):
                    renameInstalledPath(
                        mods_directory + "/~" + filedata, mods_directory + "/" + filedata, modDirectory=True
                    )
            self.enabled = True
        return incomplete

    def disable(self):
        if self.enabled:
            self.uninstallXmlKeys()
            self.uninstallMenus()
            for menu in iter(self.menus):
                if path.exists(data.getConfig().menu + "/" + menu) and not menu.endswith(".disabled"):
                    renameInstalledPath(
                        data.getConfig().menu + "/" + menu,
                        data.getConfig().menu + "/" + menu + ".disabled",
                        modDirectory=False,
                    )
            for dlc in iter(self.dlcs):
                dlc_directory = data.getConfig().dlc
                if dlc_directory is None:
                    raise ValueError("No game directory configured for DLC files")
                if path.exists(dlc_directory + "/" + dlc):
                    for subdir, _, fls in walk(dlc_directory + "/" + dlc):
                        for file in fls:
                            if not file.endswith(".disabled") and not file.startswith("."):
                                renameInstalledPath(
                                    path.join(subdir, file), path.join(subdir, file) + ".disabled", modDirectory=True
                                )
            for filedata in iter(self.files):
                mods_directory = data.getConfig().mods
                if mods_directory is None:
                    raise ValueError("No game directory configured for mod files")
                if path.exists(mods_directory + "/" + filedata):
                    if not filedata.startswith("~"):
                        renameInstalledPath(
                            mods_directory + "/" + filedata,
                            mods_directory + "/~" + filedata,
                            modDirectory=True,
                        )
            self.enabled = False

    def checkPriority(self):
        if not self.priority:
            for filedata in iter(self.files):
                if data.getConfig().priority.has_section(filedata):
                    self.priority = data.getConfig().getPriority(filedata)

    def installMenus(self):
        self.updateMenuFileLists(install=True)

    def updateMenuFileLists(self, install: bool):
        if not self.menus or not data.getConfig().menu:
            return
        for filename in ('dx11filelist.txt', 'dx12filelist.txt'):
            filelist = path.join(data.getConfig().menu, filename)
            if not path.isfile(filelist):
                continue
            filelist = checkInstalledPath(filelist, modDirectory=False)
            with open(filelist, 'r', encoding=detectEncoding(filelist)) as userfile:
                original = userfile.read().splitlines()
            lines = list(original)
            for menu in self.menus:
                entry = menu + ';'
                if install:
                    if entry.casefold() not in {line.strip().casefold() for line in lines}:
                        lines.append(entry)
                else:
                    lines = [line for line in lines if line.strip().casefold() != entry.casefold()]
            if lines != original:
                with atomicWrite(filelist, 'w', encoding='utf-16') as userfile:
                    userfile.write('\n'.join(lines) + '\n')

    def installXmlKeys(self):
        if self.xmlkeys:
            input_file = checkInstalledPath(path.join(data.getConfig().menu, "input.xml"), modDirectory=False)
            text = ''
            with open(input_file, "r", encoding=detectEncoding(input_file)) as userfile:
                text = userfile.read()
            for xml in iter(self.xmlkeys):
                if xml not in text:
                    text = text.replace(
                        "<!-- [BASE_CharacterMovement] -->", xml + "\n<!-- [BASE_CharacterMovement] -->"
                    )
            with atomicWrite(input_file, "w", encoding="utf-16") as userfile:
                userfile.write(text)
        if self.hidden:
            hidden_file = checkInstalledPath(path.join(data.getConfig().menu, "hidden.xml"), modDirectory=False)
            text = ''
            with open(
                hidden_file,
                "r",
                encoding=detectEncoding(hidden_file),
            ) as userfile:
                text = userfile.read()
            for xml in iter(self.hidden):
                if xml not in text:
                    text = text.replace("</VisibleVars>", xml + "\n</VisibleVars>")
            with atomicWrite(hidden_file, "w", encoding="utf-16") as userfile:
                userfile.write(text)

    def uninstallMenus(self):
        self.updateMenuFileLists(install=False)

    def uninstallXmlKeys(self):
        if (self.xmlkeys) and path.exists(data.getConfig().menu + "/input.xml"):
            input_file = checkInstalledPath(path.join(data.getConfig().menu, "input.xml"), modDirectory=False)
            text = ''
            with open(input_file, "r", encoding=detectEncoding(input_file)) as userfile:
                text = userfile.read()
            for xml in iter(self.xmlkeys):
                if xml in text:
                    text = text.replace(xml + "\n", '')
            with atomicWrite(input_file, "w", encoding="utf-16") as userfile:
                userfile.write(text)
        if (self.hidden) and path.exists(data.getConfig().menu + "/hidden.xml"):
            hidden_file = checkInstalledPath(path.join(data.getConfig().menu, "hidden.xml"), modDirectory=False)
            text = ''
            with open(
                hidden_file,
                "r",
                encoding=detectEncoding(hidden_file),
            ) as userfile:
                text = userfile.read()
            for xml in iter(self.hidden):
                if xml in text:
                    text = text.replace(xml + "\n", '')
            with atomicWrite(hidden_file, "w", encoding="utf-16") as userfile:
                userfile.write(text)

    def installInputKeys(self) -> Tuple[int, int]:
        from src.core.fetcher import fetchInputSettings

        print("installing input settings", str(self.inputsettings))
        added = 0
        skipped = 0
        existing: List[Key] = []
        filename = data.getConfig().settings + "/input.settings"
        if path.exists(filename):
            with open(filename, 'r', encoding=detectEncoding(filename)) as userfile:
                text = userfile.read()
                existing = fetchInputSettings(text)
        conflicts: List[Tuple[Key, List[Key]]] = []
        if self.inputsettings:
            for key in iter(self.inputsettings):
                if any(x for x in existing if x == key):
                    continue
                conflicting = [
                    x
                    for x in existing
                    if not x.empty
                    and x.action is not None
                    and key.action is not None
                    and x.context == key.context
                    and x.action["Action"] == key.action["Action"]
                    and ((x.type == key.type and x.key != key.key) or (x.key == key.key and x.action != key.action))
                ]
                if len(conflicting) == 0:
                    added += 1
                    existing.append(key)
                else:
                    conflicts.append((key, conflicting))
        if conflicts:
            saved = None
            for key, conflicting in conflicts:
                print("conflicting key", key, conflicting)
                for e in conflicting:
                    justModifiers = e.key == key.key and e.action != key.action
                    if saved is None:
                        msg = MessageRebindKeys(e, key, e.context, justModifiers)
                    else:
                        msg = saved
                    if msg == QMessageBox.StandardButton.Yes:
                        existing.remove(e)
                        existing.append(key)
                        added += 1
                    elif msg == QMessageBox.StandardButton.No:
                        skipped += 1
                    elif msg == QMessageBox.StandardButton.YesToAll:
                        existing.remove(e)
                        existing.append(key)
                        added += 1
                        saved = QMessageBox.StandardButton.Yes
                    elif msg == QMessageBox.StandardButton.NoToAll:
                        skipped += 1
                        saved = QMessageBox.StandardButton.No
        existing.sort()
        text = ''
        category = None
        for key in existing:
            if key.context != category:
                if category is not None:
                    text += '\n'
                category = key.context
                if not category.startswith('['):
                    text += '['
                text += category
                if not category.endswith(']'):
                    text += ']'
                text += '\n'
            if not key.empty:
                text += repr(key) + "\n"
        with open(filename, 'w', encoding="utf-8") as userfile:
            userfile.write(text)
            userfile.flush()
            os.fsync(userfile.fileno())

        return added, skipped

    def installUserSettings(self) -> int:
        added = 0
        if self.usersettings:
            added = self.installUserSettingsToFile("user.settings")

            if data.getConfig().gameversion in ("ng", "re"):
                dx12AdditionCount = self.installUserSettingsToFile("dx12user.settings")
                if added != dx12AdditionCount:
                    raise Exception(
                        self.name
                        + " failed to install same number of user settings to dx11 and dx12 user.settings files dx11 count: "
                        + str(added)
                        + "dx12 count: "
                        + str(dx12AdditionCount)
                    )
        return added

    def installUserSettingsToFile(self, fileName) -> int:
        added = 0
        absFilePath = data.getConfig().settings + "/" + fileName
        config = CaseSensitiveConfigParser(strict=False)
        if path.exists(absFilePath):
            config.read(absFilePath, encoding=detectEncoding(absFilePath))
        for setting in iter(self.usersettings):
            if not config.has_section(setting.context):
                config.add_section(setting.context)
            config.set(setting.context, setting.option, setting.value)
            added += 1
        with atomicWrite(absFilePath, 'w', encoding="utf-8", follow_symlinks=True) as userfile:
            config.write(userfile, space_around_delimiters=False)
        return added

    def uninstallUserSettings(self):
        if self.usersettings:
            self.uninstallUserSettingsFromFile("user.settings")

            if data.getConfig().gameversion in ("ng", "re"):
                self.uninstallUserSettingsFromFile("dx12user.settings")

    def uninstallUserSettingsFromFile(self, fileName):
        absFilePath = data.getConfig().settings + "/" + fileName
        if not path.exists(absFilePath):
            return
        config = CaseSensitiveConfigParser(strict=False)
        config.read(absFilePath, encoding=detectEncoding(absFilePath))
        for setting in iter(self.usersettings):
            if config.has_section(setting.context):
                config.remove_option(setting.context, setting.option)
        with atomicWrite(absFilePath, 'w', encoding="utf-8", follow_symlinks=True) as userfile:
            config.write(userfile, space_around_delimiters=False)

    def __repr__(self):
        string = (
            translate("MOD", "NAME: ")
            + str(self.name)
            + "\n"
            + translate("MOD", "ENABLED: ")
            + str(self.enabled)
            + "\n"
            + translate("MOD", "PRIORITY: ")
            + self.priority
            + "\n"
        )
        if self.files:
            string += "\n" + translate("MOD", "DATA:") + "\n"
            for file in iter(self.files):
                string += file + "\n"
        if self.dlcs:
            string += "\n" + translate("MOD", "DLC:") + "\n"
            for dlc in iter(self.dlcs):
                string += dlc + "\n"
        if self.menus:
            string += "\n" + translate("MOD", "MENUS:") + "\n"
            for menu in iter(self.menus):
                string += menu + "\n"
        if self.xmlkeys:
            string += "\n" + translate("MOD", "XML VARIABLES:") + "\n"
            for xml in iter(self.xmlkeys):
                string += xml + "\n"
        if self.hidden:
            string += "\n" + translate("MOD", "HIDDEN XML:") + "\n"
            for xml in iter(self.hidden):
                string += xml + "\n"
        if self.inputsettings:
            string += "\n" + translate("MOD", "INPUT KEYS:") + "\n"
            context = ''
            for elem in iter(self.inputsettings):
                if elem.context != context:
                    if context != "":
                        string += '\n'
                    context = elem.context
                    string += context + '\n'
                string += str(elem) + "\n"
        if self.usersettings:
            string += "\n" + translate("MOD", "USER SETTINGS:") + "\n"
            context = ''
            for elem in iter(self.usersettings):
                if elem.context != context:
                    if context != "":
                        string += '\n'
                    context = elem.context
                    string += '[' + context + ']' + '\n'
                string += str(elem) + "\n"
        if self.readmes:
            string += "\n" + translate("MOD", "READMES:") + "\n"
            for readme in iter(self.readmes):
                string += readme + "\n"
        return string
