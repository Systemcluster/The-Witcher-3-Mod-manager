import configparser
import os
import shutil as files
import sys
import xml.etree.ElementTree as XML
import ctypes.wintypes
from distutils import dir_util as dirs
import re
from PyQt5 import QtWidgets, QtCore, QtGui

config = configparser.ConfigParser(allow_no_value=True, delimiters='=')
priority = configparser.ConfigParser()
priority.optionxform = str
buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
documents = str(buf.value).replace('\\', '/')
manager = documents + '/The Witcher 3 Mod Manager'

def initconfig():
    '''Creates or reads existing configuration'''
    if (not os.path.exists(manager)):
        os.mkdir(manager)
    config.read(manager+'/config.ini')
    priority.read(documents+'/The Witcher 3/mods.settings')

def getini(section, option):
    '''Gets option value from configuration if exists'''
    if (config.has_option(section,option)):
        return config.get(section, option)
    else:
        return ""

def getpriority(modfile):
    '''Gets mod priority if exists'''
    if (modfile in priority.sections()):
        return priority[modfile]['Priority']
    else:
        return None

def setpriority(modfile, value):
    '''Sets mod priority'''
    if (priority.has_section(modfile) == False):
        priority.add_section(modfile)
        priority.set(modfile, 'Enabled', '1')
    priority.set(modfile, 'Priority', value)

def setini(section, option, value):
    '''Sets option value to configuration'''
    if (config.has_section(section) == False):
        config.add_section(section)
    config.set(section,option,value)
    iniwrite()

def setininovalue(section, value):
    '''Sets option that has no value to configuration'''
    config.set(section, value)
    iniwrite()

def getininovalue(section):
    '''Gets option that has no value from configuration'''
    list = []
    for value in config.items(section):
        list.append(value[0])
    return list

def removeininovalue(section, value):
    '''Removes all options that have no values from configuration'''
    if (config.has_section(section)):
        config.remove_option(section, value)
    iniwrite()

def iniwrite():
    '''Saves configuration to disk to documents/The Witcher 3 Mod Manager/config.ini file'''
    with open(manager+'/config.ini', 'w') as configfile:
        config.write(configfile)

def savewindowsettings(ui):
    setini('WINDOW', 'width', str(ui.width()))
    setini('WINDOW', 'height', str(ui.height()))

def prioritywrite():
    '''Saves priority data to disk - documents/The Witcher 3/mods.settings file'''
    with open(documents+'/The Witcher 3/mods.settings', 'w') as configfile:
        priority.write(configfile)
    text = ''
    with open(documents+'/The Witcher 3/mods.settings', 'r') as configfile:
        text = configfile.read()
    with open(documents+'/The Witcher 3/mods.settings', 'w') as configfile:
        text = text.replace(' = ', '=')
        configfile.write(text)


def restart_program():
    '''Restarts the program'''
    iniwrite()
    python = sys.executable
    os.execl(python, python, *sys.argv)

def copyfolder(src, dest):
    if (not os.path.exists(dest)):
        files.copytree(src, dest)
    else:
        dirs.copy_tree(src, dest)


class FileDialog(QtWidgets.QFileDialog):
    def __init__(self, *args):
        super(FileDialog, self).__init__(*args)
        self.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
        self.tree = self.findChild(QtWidgets.QTreeView)
        self.resize(800, 800)
        self.selectedFiles = None
        self.exec_()

    def accept(self):
        inds = self.tree.selectionModel().selectedRows(0)
        self.selectedFiles = []
        for i in inds:
            self.selectedFiles.append(str(self.directory().absolutePath()) + "/" + str(i.data()))
        self.close()

def getFile(directory="", extensions="", title="Select Files or Folders"):
    '''Opens custom dialog for selecting multiple folders or files'''
    return FileDialog(None, title, str(directory), str(extensions)).selectedFiles

def indent(elem, level=0):
    '''Beautify the xml'''
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def saveXML(modlist):
    '''Saves installation mod data to disk to documents/The Witcher 3 Mod Manager/installed.xml'''
    root = XML.Element('installed')
    for mod in modlist.values():
        root = mod.writeToXml(root)
    indent(root)
    tree = XML.ElementTree(root)
    tree.write(manager+'/installed.xml')

def get_size(start_path = '.'):
    '''Calculates the size of the selected folder'''
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

class Ui_Details(object):
    '''Dialog showing mod details'''
    def setupUi(self, Details, text):
        Details.setObjectName("Details")
        Details.resize(700, 800)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Details)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Details)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setPlainText(text)
        self.plainTextEdit.setReadOnly(True)
        self.horizontalLayout.addWidget(self.plainTextEdit)

        self.retranslateUi(Details)
        QtCore.QMetaObject.connectSlotsByName(Details)

    def retranslateUi(self, Details):
        _translate = QtCore.QCoreApplication.translate
        Details.setWindowTitle(_translate("Details", "Details"))

def getIcon(str):
    '''Gets icon from the res folder'''
    icon = QtGui.QIcon()
    icon.addFile('res/' + str)
    return icon

def getKey(item):
    '''Helper function for the mod list'''
    return item[1]


def isData(name):
    '''Checks if given name represents correct mod folder or not'''
    return re.match(r"^(~|)mod.+$", name)