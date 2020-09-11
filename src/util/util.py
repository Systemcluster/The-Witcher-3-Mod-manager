'''Global Helpers'''
# pylint: disable=invalid-name,superfluous-parens,missing-docstring,wildcard-import,unused-wildcard-import

from sys import platform
import os
import sys
import re
import traceback
import webbrowser
import subprocess
from shutil import copytree, rmtree
from platform import python_version
from configparser import ConfigParser
from threading import Timer
import cchardet

from PySide2 import QtGui, QtCore, __version__
from PySide2.QtWidgets import QFileDialog, QMessageBox, QWidget

from src.globals import data
from src.globals.constants import *
from src.gui.file_dialog import FileDialog
from src.gui.alerts import MessageCouldntOpenFile, MessageNotConfigured, MessageUnsupportedOS


def formatUserError(error: Exception) -> str:
    print(traceback.format_exc(), error, file=sys.stderr)
    if data.debug:
        return traceback.format_exc() + str(error)
    else:
        return str(error)


def getDocumentsFolder() -> str:
    path = ""
    if platform == "win32" or platform == "cygwin":
        from ctypes import create_unicode_buffer, wintypes, windll
        buf = create_unicode_buffer(wintypes.MAX_PATH)
        windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
        path = normalizePath(buf.value)
    elif platform == "linux" or platform == "darwin":
        # try steam proton documents location path
        path = normalizePath(os.path.expanduser(
            "~/.local/share/Steam/steamapps/compatdata/292030/pfx/drive_c/users/steamuser/My Documents"))
    else:
        MessageUnsupportedOS(platform)
        sys.exit(1)
    if not path or not os.path.exists(path):
        path = normalizePath(str(QFileDialog.getExistingDirectory(
            None,
            "Select \"My Documents\" directory containing the Witcher 3 config directory",
            "My Documents")))
    return path


def getConfigFolder() -> str:
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
    MessageNotConfigured()
    gamePath = str(QFileDialog.getOpenFileName(
        None,
        TRANSLATE("MainWindow", "Select witcher3.exe"),
        data.config.gameexe or "witcher3.exe",
        "*.exe")[0])
    try:
        data.config.game = gamePath
    except ValueError as err:
        print(str(err), file=sys.stderr)
        QMessageBox.critical(
            None,
            TRANSLATE("MainWindow", "Selected file not correct"),
            TRANSLATE("MainWindow", "'witcher3.exe' file not selected"),
            QMessageBox.StandardButton.Ok)
        return False
    return True


def reconfigureScriptMergerPath():
    mergerPath = str(QFileDialog.getOpenFileName(
        None,
        TRANSLATE("MainWindow", "Select script merger .exe"),
        data.config.scriptmerger or '',
        "*.exe")[0])
    if mergerPath:
        data.config.scriptmerger = mergerPath


def showAboutWindow():
    QMessageBox.about(
        None,
        TRANSLATE("MainWindow", "About"),
        TRANSLATE(
            "MainWindow",
            ""+TITLE+"\n"
            "Version: "+VERSION+"\n"
            "Authors: "+(", ".join(AUTHORS))+"\n"
            "\n"
            "Written in: Python "+python_version()+"\n"
            "GUI: PySide2 "+__version__+"\n"
            "\n"
            "Thank you for using "+TITLE+"!"))


def openUrl(url: str):
    webbrowser.open(url)


def openFile(path: str):
    try:
        if isExecutable(path):
            directory, _ = os.path.split(path)
            subprocess.Popen([path], cwd=directory)
        elif os.path.isfile(path):
            if platform == "linux" or platform == "darwin":
                try:
                    subprocess.call(["xdg-open", path])
                except OSError as e:
                    editor = os.getenv('EDITOR')
                    if editor:
                        subprocess.Popen([editor, path])
                    else:
                        webbrowser.open(path, new=1)
            else:
                try:
                    os.startfile(path)
                except Exception as e:
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
        except OSError as e:
            webbrowser.open(path, new=1)
    else:
        os.startfile(path, "explore")


def copyFolder(src, dst):
    '''Copy folder from src to dst'''
    dst = os.path.normpath(dst)
    src = os.path.normpath(src)
    print(
        f'copying from {src} to {dst} (exists: {os.path.isdir(os.path.normpath(dst))})')
    rmtree(dst, ignore_errors=True)
    while os.path.isdir(dst):
        pass
    copytree(src, dst)


def restartProgram():
    '''Restarts the program'''
    data.config.write()
    python = sys.executable
    os.execl(python, python, *sys.argv)


def getFile(directory="", extensions="", title="Select Files or Folders"):
    '''Opens custom dialog for selecting multiple folders or files'''
    return FileDialog(None, title, str(directory), str(extensions)).selectedFiles


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
    if os.path.exists(path):
        with open(path, 'rb') as file:
            text = file.read()
            detected = cchardet.detect(text)
            print("detected", path, "as", detected)
            return detected["encoding"]
    else:
        return "utf-8"


def fixUserSettingsDuplicateBrackets():
    '''Fix invalid section names in user.settings'''
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


def debounce(ms: int):
    """Debounce a functions execution by {ms} milliseconds"""
    def decorator(fun):
        def debounced(*args, **kwargs):
            def deferred():
                fun(*args, **kwargs)
            try:
                debounced.timer.cancel()
            except AttributeError:
                pass
            debounced.timer = Timer(ms / 1000.0, deferred)
            debounced.timer.start()
        return debounced
    return decorator
