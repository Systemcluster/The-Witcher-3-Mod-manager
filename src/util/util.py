'''Global Helpers'''
#pylint: disable=invalid-name,superfluous-parens

import os
import sys
import re
import configparser
import ctypes.wintypes
import xml.etree.ElementTree as XML
from shutil import copytree
from distutils import dir_util

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QTreeView, QHBoxLayout, QPlainTextEdit

config = configparser.ConfigParser(allow_no_value=True, delimiters='=')
priority = configparser.ConfigParser()
priority.optionxform = str
buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)
documents = str(os.path.normpath(buf.value)).replace('\\', '/')

def initconfig():
    '''Creates or reads existing configuration'''
    config.read('config.ini')
    priority.read(documents+'/The Witcher 3/mods.settings')

def getini(section, option):
    '''Gets option value from configuration if exists'''
    if (config.has_option(section, option)):
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
    if (not priority.has_section(modfile)):
        priority.add_section(modfile)
        priority.set(modfile, 'Enabled', '1')
    priority.set(modfile, 'Priority', value)

def setini(section, option, value):
    '''Sets option value to configuration'''
    if (not config.has_section(section)):
        config.add_section(section)
    config.set(section, option, value)
    iniwrite()

def setininovalue(section, value):
    '''Sets option that has no value to configuration'''
    config.set(section, value)
    iniwrite()

def getininovalue(section):
    '''Gets option that has no value from configuration'''
    valuelist = []
    for value in config.items(section):
        valuelist.append(value[0])
    return valuelist

def removeininovalue(section, value):
    '''Removes all options that have no values from configuration'''
    if (config.has_section(section)):
        config.remove_option(section, value)
    iniwrite()

def iniwrite():
    '''Saves configuration to disk to documents/The Witcher 3 Mod Manager/config.ini file'''
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def savewindowsettings(ui, window):
    '''Saves the window settings in the ini file'''
    setini('WINDOW', 'width', str(window.width()))
    setini('WINDOW', 'height', str(window.height()))
    setini('WINDOW', 'section0', str(ui.treeWidget.header().sectionSize(0)))
    setini('WINDOW', 'section1', str(ui.treeWidget.header().sectionSize(1)))
    setini('WINDOW', 'section2', str(ui.treeWidget.header().sectionSize(2)))
    setini('WINDOW', 'section3', str(ui.treeWidget.header().sectionSize(3)))
    setini('WINDOW', 'section4', str(ui.treeWidget.header().sectionSize(4)))
    setini('WINDOW', 'section5', str(ui.treeWidget.header().sectionSize(5)))
    setini('WINDOW', 'section6', str(ui.treeWidget.header().sectionSize(6)))
    setini('WINDOW', 'section7', str(ui.treeWidget.header().sectionSize(7)))
    setini('WINDOW', 'section8', str(ui.treeWidget.header().sectionSize(8)))
    setini('WINDOW', 'section9', str(ui.treeWidget.header().sectionSize(9)))
    setini('WINDOW', 'section10', str(ui.treeWidget.header().sectionSize(10)))
    setini('WINDOW', 'section11', str(ui.treeWidget.header().sectionSize(11)))

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

def copyfolder(src, dst):
    '''Copy folder from src to dst'''
    if (not os.path.exists(dst)):
        copytree(src, dst)
    else:
        dir_util.copy_tree(src, dst)


class FileDialog(QFileDialog):
    '''Custom FileDialog'''
    def __init__(self, *args):
        super(FileDialog, self).__init__(*args)
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.ExistingFiles)
        self.tree = self.findChild(QTreeView)
        self.resize(800, 800)
        self.selectedFiles = None
        self.horizontalLayout = None
        self.exec_()

    def accept(self):
        '''Accept selected files'''
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
    if elem:
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
    tree.write('installed.xml')

def get_size(start_path='.'):
    '''Calculates the size of the selected folder'''
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

class DetailsDialog:
    '''Dialog showing mod details'''

    def __init__(self):
        self.horizontalLayout = None
        self.plainTextEdit = None

    def setupUi(self, Details, text):
        '''Setup UI'''
        Details.setObjectName("Details")
        Details.resize(700, 800)
        self.horizontalLayout = QHBoxLayout(Details)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plainTextEdit = QPlainTextEdit(Details)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setPlainText(text)
        self.plainTextEdit.setReadOnly(True)
        self.horizontalLayout.addWidget(self.plainTextEdit)

        self.retranslateUi(Details)
        QtCore.QMetaObject.connectSlotsByName(Details)

    def retranslateUi(self, Details):
        '''Retranslate UI'''
        _translate = QtCore.QCoreApplication.translate
        Details.setWindowTitle(_translate("Details", "Details"))

def getIcon(filename):
    '''Gets icon from the res folder'''
    icon = QtGui.QIcon()
    icon.addFile('res/' + filename)
    return icon

def getKey(item):
    '''Helper function for the mod list'''
    return item[1]


def isData(name):
    '''Checks if given name represents correct mod folder or not'''
    return re.match(r"^(~|)mod.+$", name)
