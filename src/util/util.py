'''Global Helpers'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring,wildcard-import,unused-wildcard-import,import-outside-toplevel

import os
import re
import subprocess
import sys
import traceback
import webbrowser
from configparser import ConfigParser
from platform import python_version
from shutil import copytree, rmtree
from sys import platform
from threading import Timer
from typing import Any, Callable

from PySide6 import QtGui, __version__
from PySide6.QtWidgets import QFileDialog, QMessageBox


def formatUserError(error: Exception) -> str:
    from src.globals import data
    print(traceback.format_exc(), error, file=sys.stderr)
    if data.debug:
        return traceback.format_exc() + str(error)
    else:
        return str(error)


def getDocumentsFolder() -> str:
    from src.globals.constants import translate
    from src.gui.alerts import MessageUnsupportedOS
    path = ""
    if platform == "win32" or platform == "cygwin":
        from ctypes import create_unicode_buffer, windll, wintypes
        buf = create_unicode_buffer(wintypes.MAX_PATH)
        windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        path = normalizePath(buf.value)
    elif platform == "linux" or platform == "darwin":
        # try steam proton documents path default (1)
        path = normalizePath(os.path.expanduser(
            "~/.local/share/Steam/steamapps/compatdata/292030/pfx/drive_c/users/steamuser/My Documents"))
        if not path or not os.path.exists(path):
            # try steam proton documents path default (2)
            path = normalizePath(os.path.expanduser(
                "~/.steam/steam/steamapps/compatdata/292030/pfx/drive_c/users/steamuser/My Documents"))
        if not path or not os.path.exists(path):
            # try steam proton documents path on steam deck internal storage
            path = normalizePath(
                "/home/deck/.local/share/Steam/steamapps/compatdata/292030/pfx/drive_c/users/steamuser/My Documents")
        if not path or not os.path.exists(path):
            # try steam proton documents path on steam deck sd card
            path = normalizePath(
                "/run/media/mmcblk0p1/steamapps/compatdata/292030/pfx/drive_c/users/steamuser/My Documents")
    else:
        MessageUnsupportedOS(platform)
        sys.exit(1)
    if not path or not os.path.exists(path):
        dialog = QFileDialog(None, translate("MainWindow", "Select \"My Documents\" directory containing the Witcher 3 config directory"), "My Documents")
        dialog.setOptions(QFileDialog.Option.DontUseNativeDialog)
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            path = normalizePath(str(dialog.selectedFiles()[0]))
    return path


def getConfigFolder() -> str:
    from src.gui.alerts import MessageUnsupportedOS
    if platform == "win32" or platform == "cygwin":
        return getDocumentsFolder()
    if platform == "linux" or platform == "darwin":
        return normalizePath(os.path.expanduser("~/.config"))
    MessageUnsupportedOS(platform)
    sys.exit(1)


def getConfigFolderName() -> str:
    if platform == "linux" or platform == "darwin":
        return "TheWitcher3ModManager"
    return "The Witcher 3 Mod Manager"


def getVersionString() -> str:
    from src.globals.constants import TITLE, VERSION
    return TITLE + " " + VERSION


def getProgramRootFolder() -> str:
    if getattr(sys, 'frozen', False):
        # The application is frozen
        return normalizePath(os.path.dirname(sys.executable))
    else:
        return normalizePath(os.path.dirname(os.path.abspath(__file__))+"/../../")


def normalizePath(path: str) -> str:
    return os.path.normpath(str(path)).replace('\\', '/')


def reconfigureGamePath() -> bool:
    from src.globals import data
    from src.globals.constants import translate
    from src.gui.alerts import MessageNotConfigured
    MessageNotConfigured()
    dialog = QFileDialog(
        None,
        translate("MainWindow", "Select witcher3.exe"),
        data.config.gameexe or "witcher3.exe",
        "*.exe")
    dialog.setOptions(QFileDialog.Option.DontUseNativeDialog)
    if dialog.exec():
        gamePath = normalizePath(str(dialog.selectedFiles()[0]))
        try:
            data.config.gameexe = gamePath
        except ValueError as err:
            print(str(err), file=sys.stderr)
            QMessageBox.critical(
                None,
                translate("MainWindow", "Selected file not correct"),
                translate("MainWindow", "'witcher3.exe' file not selected"),
                QMessageBox.StandardButton.Ok)
            return False
        return True
    return False


def reconfigureScriptMergerPath():
    from src.globals import data
    from src.globals.constants import translate
    from src.gui.alerts import MessageNotConfiguredScriptMerger
    MessageNotConfiguredScriptMerger()
    dialog = QFileDialog(
        None,
        translate("MainWindow", "Select WitcherScriptMerger.exe"),
        data.config.scriptmerger or '',
        "*.exe")
    dialog.setOptions(QFileDialog.Option.DontUseNativeDialog)
    if dialog.exec():
        mergerPath = normalizePath(str(dialog.selectedFiles()[0]))
        if mergerPath:
            data.config.scriptmerger = mergerPath


def showAboutWindow():
    from src.globals.constants import AUTHORS, TITLE, VERSION, translate
    QMessageBox.about(
        None,
        translate("MainWindow", "About"),
        ""+TITLE+"\n" +
        translate("MainWindow", "Version: ")+VERSION+"\n" +
        translate("MainWindow", "Authors: ")+(", ".join(AUTHORS))+"\n" +
        "\n" +
        translate("MainWindow", "Written in: ")+"Python "+python_version()+"\n" +
        translate("MainWindow", "GUI: PySide6 ")+__version__+"\n" +
        "\n" +
        translate("MainWindow", "Thank you for using ")+TITLE+translate("MainWindow", "!"))


def openUrl(url: str):
    webbrowser.open(url)


def openFile(path: str):
    from src.gui.alerts import MessageCouldntOpenFile
    try:
        if isExecutable(path):
            directory, _ = os.path.split(path)
            subprocess.Popen([path], cwd=directory)
        elif os.path.isfile(path):
            if platform == "linux" or platform == "darwin":
                try:
                    subprocess.call(["xdg-open", path])
                except OSError:
                    editor = os.getenv('EDITOR')
                    if editor:
                        subprocess.Popen([editor, path])
                    else:
                        webbrowser.open(path, new=1)
            else:
                try:
                    os.startfile(path)
                except Exception:
                    webbrowser.open(path, new=1)
        elif os.path.isdir(path):
            openFolder(path)
        else:
            raise FileNotFoundError(path)
    except Exception as e:
        MessageCouldntOpenFile(path, formatUserError(e))


def openFolder(path: str):
    while path and not os.path.isdir(path):
        path, _ = os.path.split(path)
    if platform == "linux" or platform == "darwin":
        try:
            subprocess.Popen(["xdg-open", path])
        except OSError:
            webbrowser.open(path, new=1)
    else:
        os.startfile(path, "explore")


def copyFolder(src, dst):
    '''Copy folder from src to dst'''
    dst = os.path.normpath(dst)
    src = os.path.normpath(src)
    print(
        f'copying from {src} to {dst} (exists: {os.path.isdir(os.path.normpath(dst))})')
    removeDirectory(dst)
    while os.path.isdir(dst):
        pass
    copytree(src, dst)


def removeDirectory(directory: str) -> None:
    def getWriteAccess(func: Callable, directory: str, exc_info: Any) -> None:
        import stat
        os.chmod(directory, stat.S_IWRITE)
        func(directory)
    if os.path.isdir(directory):
        rmtree(directory, onerror=getWriteAccess)


def restartProgram():
    '''Restarts the program'''
    from src.globals import data
    data.config.write_priority().join()
    data.config.write_config().join()
    python = sys.executable
    os.execl(python, python, *sys.argv)


def getFile(parent=None, directory="", extensions="", title=None) -> list[str]:
    '''Opens custom dialog for selecting multiple folders or files'''
    from src.globals.constants import translate
    if title is None:
        title = translate("MainWindow", "Select Files or Folders")
    dialog = QFileDialog(parent, title, directory, extensions)
    dialog.setOptions(QFileDialog.Option.ReadOnly | 
                     QFileDialog.Option.DontUseNativeDialog |
                     QFileDialog.Option.HideNameFilterDetails)
    dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    dialog.setModal(True)
    dialog.open()
    result = []
    if dialog.exec():
        result = dialog.selectedFiles()
    return [normalizePath(file) for file in result if os.path.isfile(file)]


def getSize(start_path='.'):
    '''Calculates the size of the selected folder'''
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def getIcon(filename):
    '''Gets icon from the res folder'''
    icon = QtGui.QIcon()
    icon.addFile(getProgramRootFolder() + '/res/' + filename)
    return icon


def getKey(item):
    '''Helper function for the mod list'''
    return item[1]


def isData(name):
    '''Checks if given name represents correct mod folder or not'''
    return re.match(r"^(~|)mod.+$", name)


def isExecutable(name: str) -> bool:
    _, ext = os.path.splitext(name)
    return ext in ('.exe', '.bat')


def translateToChosenLanguage() -> bool:
    from src.globals import data
    language = data.config.language
    if (language and os.path.exists("translations/" + language)):
        print("loading translation", language)
        data.translator.load("translations/" + language)
        if not data.app.installTranslator(data.translator):
            print("loading translation failed", file=sys.stderr)
            return False
        return True
    else:
        print("chosen language not found:", language, file=sys.stderr)
        return False


def detectEncoding(path: str) -> str:
    import charset_normalizer
    if os.path.exists(path):
        with open(path, 'rb') as file:
            text = file.read()
            detected = charset_normalizer.detect(
                text, should_rename_legacy=True)
            print("detected", path, "as", detected)
            if detected and "encoding" in detected:
                if detected["encoding"] == "ascii":
                    return "utf-8"
                if float(detected["confidence"]) > 0.5:
                    return str(detected["encoding"])
            return "utf-8"
    else:
        return "utf-8"


def fixUserSettingsDuplicateBrackets():
    '''Fix invalid section names in user.settings'''
    from src.globals import data
    try:
        config = ConfigParser(strict=False)
        config.optionxform = str
        config.read(data.config.settings + "/user.settings",
                    encoding=detectEncoding(data.config.settings + "/user.settings"))
        for section in config.sections():
            newSection = section
            while newSection[:1] == "[":
                newSection = newSection[1:]
            while newSection[-1:] == "]":
                newSection = newSection[:-1]
            if newSection != section:
                items = config.items(section)
                if not config.has_section(newSection):
                    config.add_section(newSection)
                    for item in items:
                        config.set(newSection, item[0], item[1])
                config.remove_section(section)
        with open(data.config.settings+"/user.settings", 'w', encoding="utf-8") as userfile:
            config.write(userfile, space_around_delimiters=False)
            userfile.flush()
            os.fsync(userfile.fileno())
    except:
        print("fixing duplicate brackets failed")


def throttle(ms: int):
    """Decorator ensures function that can only be called once every `ms` milliseconds"""
    from datetime import datetime, timedelta

    def decorate(f):
        last_modified = None

        def wrapped(*args, **kwargs):
            nonlocal last_modified
            if not last_modified or datetime.now() - last_modified > timedelta(milliseconds=ms):
                result = f(*args, **kwargs)
                last_modified = datetime.now()
                return result
        return wrapped
    return decorate


def debounce(ms: int) -> Callable[[Callable[..., None]], Callable[..., Timer]]:
    """Debounce a functions execution by {ms} milliseconds"""
    def decorator(fun: Callable[..., None]) -> Callable[..., Timer]:
        def debounced(*args: Any, **kwargs: Any) -> Timer:
            def deferred():
                fun(*args, **kwargs)
            try:
                debounced.timer.cancel()
            except AttributeError:
                pass
            debounced.timer = Timer(ms / 1000.0, deferred)
            debounced.timer.start()
            return debounced.timer
        return debounced
    return decorator
