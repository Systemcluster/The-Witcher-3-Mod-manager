'''Main Widget'''
# pylint: disable=invalid-name,superfluous-parens,wildcard-import,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring,too-many-lines

from os import path
from platform import python_version
import subprocess
import webbrowser

import xml.etree.ElementTree as XML

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, QFileInfo, QRect, QMetaObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QTreeWidget, \
    QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QAction, QInputDialog, QLineEdit, \
    QFileIconProvider, QAbstractItemView, QTextEdit, QSizePolicy, QMenu, QProgressBar, \
    QMenuBar, QToolBar, QActionGroup, QMessageBox

from src.globals.constants import *
from src.globals import data
from src.util.util import *
from src.util.syntax import *
from src.domain.mod import Mod
from src.gui.tree_widget import CustomTreeWidgetItem
from src.gui.details_dialog import DetailsDialog
from src.gui.alerts import MessageAlertScript


class CustomMainWidget(QWidget):
    '''Main Widget'''

    def __init__(self, parent):
        super().__init__(parent)
        self.mainWindow = parent

        try:
            self.mainWindow.setObjectName("MainWindow")

            wini = int(data.config.get('WINDOW', 'width')) \
                if data.config.get('WINDOW', 'width') else 1024
            hini = int(data.config.get('WINDOW', 'height')) \
                if data.config.get('WINDOW', 'height') else 720

            self.mainWindow.resize(wini, hini)
            self.mainWindow.setCursor(QCursor(Qt.ArrowCursor))
            self.mainWindow.setWindowOpacity(1.0)
            self.mainWindow.setStatusTip("")
            self.mainWindow.setAutoFillBackground(False)
            self.mainWindow.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.mainWindow.setAcceptDrops(True)

            self.centralwidget = QWidget(self.mainWindow)
            self.centralwidget.setObjectName("centralwidget")

            self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
            self.verticalLayout_2.setObjectName("verticalLayout_2")

            self.treeWidget = QTreeWidget(self.centralwidget)
            self.treeWidget.setMinimumSize(QSize(750, 500))
            self.treeWidget.setUniformRowHeights(True)
            self.treeWidget.setAnimated(True)
            self.treeWidget.setHeaderHidden(False)
            self.treeWidget.setColumnCount(8)
            self.treeWidget.setObjectName("treeWidget")
            self.treeWidget.header().setCascadingSectionResizes(True)
            self.treeWidget.header().setHighlightSections(False)
            self.treeWidget.header().setSortIndicatorShown(True)

            self.horizontalLayout_tree = QHBoxLayout()
            self.horizontalLayout_tree.setObjectName("horizontalLayout_tree")
            self.horizontalLayout_tree.addWidget(self.treeWidget)
            self.horizontalLayout_2 = QHBoxLayout()
            self.horizontalLayout_2.setObjectName("horizontalLayout_2")

            self.loadOrder = QTreeWidget(self.centralwidget)
            self.loadOrder.setUniformRowHeights(True)
            self.loadOrder.setAnimated(True)
            self.loadOrder.setHeaderHidden(False)
            self.loadOrder.setColumnCount(2)
            self.loadOrder.setObjectName("loadOrder")
            self.loadOrder.setMinimumWidth(250)
            self.loadOrder.setMaximumWidth(350)

            self.horizontalLayout_tree.addWidget(self.loadOrder)
            self.horizontalLayout_tree.setStretch(0, 3)
            self.horizontalLayout_tree.setStretch(1, 1)
            self.verticalLayout_2.addLayout(self.horizontalLayout_tree)

            self.textEdit = QTextEdit(self.centralwidget)
            self.textEdit.setMaximumSize(QSize(16777215, 16777215))
            self.textEdit.setReadOnly(True)
            self.textEdit.setObjectName("textEdit")

            self.horizontalLayout_2.addWidget(self.textEdit)
            self.verticalLayout = QVBoxLayout()
            self.verticalLayout.setObjectName("verticalLayout")

            self.pushButton_4 = QPushButton(self.centralwidget)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
            self.pushButton_4.setSizePolicy(sizePolicy)
            self.pushButton_4.setMinimumSize(QSize(250, 50))
            self.pushButton_4.setMaximumSize(QSize(350, 16777215))
            self.pushButton_4.setObjectName("pushButton_4")
            self.verticalLayout.addWidget(self.pushButton_4)
            self.pushButton_5 = QPushButton(self.centralwidget)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
            self.pushButton_5.setSizePolicy(sizePolicy)
            self.pushButton_5.setMinimumSize(QSize(250, 50))
            self.pushButton_5.setMaximumSize(QSize(350, 16777215))
            self.pushButton_5.setObjectName("pushButton_5")
            self.verticalLayout.addWidget(self.pushButton_5)
            self.horizontalLayout_2.addLayout(self.verticalLayout)
            self.horizontalLayout_2.setStretch(0, 3)
            self.horizontalLayout_2.setStretch(1, 1)
            self.verticalLayout_2.addLayout(self.horizontalLayout_2)
            self.progressBar = QProgressBar(self.centralwidget)
            self.progressBar.setProperty("value", 0)
            self.progressBar.setObjectName("progressBar")
            self.verticalLayout_2.addWidget(self.progressBar)
            self.verticalLayout_2.setStretch(0, 4)
            self.verticalLayout_2.setStretch(1, 1)

            self.mainWindow.setCentralWidget(self.centralwidget)
            self.menubar = QMenuBar(self.mainWindow)
            self.menubar.setGeometry(QRect(0, 0, 583, 21))
            self.menubar.setObjectName("menubar")
            self.menuFile = QMenu(self.menubar)
            self.menuFile.setObjectName("menuFile")
            self.menuEdit = QMenu(self.menubar)
            self.menuEdit.setObjectName("menuEdit")
            self.menuSettings = QMenu(self.menubar)
            self.menuSettings.setObjectName("menuSettings")
            self.menuSelect_Language = QMenu(self.menuSettings)
            self.menuSelect_Language.setObjectName("menuSelect_Language")
            self.menuConfigure_Settings = QMenu(self.menuSettings)
            self.menuConfigure_Settings.setObjectName("menuConfigure_Settings")
            self.menuHelp = QMenu(self.menubar)
            self.menuHelp.setObjectName("menuHelp")
            self.mainWindow.setMenuBar(self.menubar)
            self.toolBar = QToolBar(self.mainWindow)
            self.toolBar.setObjectName("toolBar")
            self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

            self.actionInstall_Mods = QAction(self.mainWindow)
            self.actionInstall_Mods.setIcon(getIcon('Add.ico'))
            self.actionInstall_Mods.setIconVisibleInMenu(False)
            self.actionInstall_Mods.setObjectName("actionInstall_Mods")
            self.actionInstall_Mods.setIconText(
                TRANSLATE('MainWindow', "Add"))
            self.actionRestore_Columns = QAction(self.mainWindow)
            self.actionRestore_Columns.setIconVisibleInMenu(False)
            self.actionRestore_Columns.setObjectName("actionRestore_Columns")
            self.actionUninstall_Mods = QAction(self.mainWindow)
            self.actionUninstall_Mods.setIcon(getIcon('rem.ico'))
            self.actionUninstall_Mods.setIconVisibleInMenu(False)
            self.actionUninstall_Mods.setObjectName("actionUninstall_Mods")
            self.actionUninstall_Mods.setIconText(
                TRANSLATE('MainWindow', "Remove"))
            self.actionEnable_Disable_Mods = QAction(self.mainWindow)
            self.actionEnable_Disable_Mods.setIcon(getIcon('check.ico'))
            self.actionEnable_Disable_Mods.setIconVisibleInMenu(False)
            self.actionEnable_Disable_Mods.setObjectName("actionEnable_Disable_Mods")
            self.actionEnable_Disable_Mods.setIconText(
                TRANSLATE('MainWindow', "Toggle"))
            self.actionRefresh_Mod_List = QAction(self.mainWindow)
            self.actionRefresh_Mod_List.setObjectName("actionRefresh_Mod_List")
            self.actionRefresh_Load_Order = QAction(self.mainWindow)
            self.actionRefresh_Load_Order.setObjectName("actionRefresh_Load_Order")
            self.actionSelect_All_Mods = QAction(self.mainWindow)
            self.actionSelect_All_Mods.setObjectName("actionSelect_All_Mods")
            self.actionSetPriority = QAction(self.mainWindow)
            self.actionSetPriority.setObjectName("actionSetPriority")
            self.actionUnsetPriority = QAction(self.mainWindow)
            self.actionUnsetPriority.setObjectName("actionUnsetPriority")
            self.actionRun_The_Game = QAction(self.mainWindow)
            self.actionRun_The_Game.setObjectName("actionRun_The_Game")
            self.actionRun_Script_Merger = QAction(self.mainWindow)
            self.actionRun_Script_Merger.setObjectName("actionRun_Script_Merger")
            self.actionAbout = QAction(self.mainWindow)
            self.actionAbout.setObjectName("actionAbout")
            self.actionRename = QAction(self.mainWindow)
            self.actionRename.setObjectName("actionRename")
            self.actionDetails = QAction(self.mainWindow)
            self.actionDetails.setObjectName("actionDetails")
            self.actionOpenFolder = QAction(self.mainWindow)
            self.actionOpenFolder.setObjectName("actionOpenFolder")
            self.actionIncreasePriority = QAction(self.mainWindow)
            self.actionIncreasePriority.setObjectName("actionIncreasePriority")
            self.actionDecreasePriority = QAction(self.mainWindow)
            self.actionDecreasePriority.setObjectName("actionDecreasePriority")
            self.actionMain_Web_Page = QAction(self.mainWindow)
            self.actionGitHub = QAction(self.mainWindow)
            self.actionMain_Web_Page.setObjectName("actionMain_Web_Page")
            self.actionGitHub.setObjectName("acitionGitHub")
            self.actionAlert_to_run_Script_Merger = QAction(self.mainWindow)
            self.actionAlert_to_run_Script_Merger.setCheckable(True)
            self.actionAlert_to_run_Script_Merger.setObjectName("actionAlert_to_run_Script_Merger")
            self.languageActionGroup = QActionGroup(self.mainWindow)
            for lang in os.listdir('translations/'):
                temp = self.makeLangAction(lang)
                self.languageActionGroup.addAction(temp)
                self.menuSelect_Language.addAction(temp)
            self.actionChange_Game_Path = QAction(self.mainWindow)
            self.actionChange_Game_Path.setObjectName("actionChange_Game_Path")
            self.actionChange_Script_Merger_Path = QAction(self.mainWindow)
            self.actionChange_Script_Merger_Path.setObjectName("actionChange_Script_Merger_Path")
            self.actionClearOutput = QAction(self.mainWindow)
            self.actionClearOutput.setObjectName("actionClearOutput")

            self.menuFile.addAction(self.actionInstall_Mods)
            self.menuFile.addAction(self.actionUninstall_Mods)
            self.menuFile.addAction(self.actionEnable_Disable_Mods)
            self.menuFile.addSeparator()
            self.menuFile.addAction(self.actionOpenFolder)
            self.menuFile.addSeparator()
            self.menuFile.addAction(self.actionRefresh_Mod_List)
            self.menuFile.addAction(self.actionRefresh_Load_Order)
            self.menuFile.addAction(self.actionSelect_All_Mods)

            self.menuConfigure_Settings.addAction(self.actionChange_Game_Path)
            self.menuConfigure_Settings.addAction(self.actionChange_Script_Merger_Path)
            self.menuConfigure_Settings.addSeparator()
            self.menuConfigure_Settings.addAction(self.actionRestore_Columns)
            self.menuConfigure_Settings.addSeparator()
            self.menuConfigure_Settings.addAction(self.actionAlert_to_run_Script_Merger)
            self.menuConfigure_Settings.addSeparator()
            self.menuSettings.addAction(self.menuConfigure_Settings.menuAction())
            self.menuSettings.addAction(self.menuSelect_Language.menuAction())

            self.menuHelp.addAction(self.actionAbout)
            self.menuHelp.addAction(self.actionMain_Web_Page)
            self.menuHelp.addAction(self.actionGitHub)
            self.menubar.addAction(self.menuFile.menuAction())
            self.menubar.addAction(self.menuEdit.menuAction())
            self.menubar.addAction(self.menuSettings.menuAction())
            self.menubar.addAction(self.menuHelp.menuAction())
            self.toolBar.addAction(self.actionInstall_Mods)
            self.toolBar.addAction(self.actionUninstall_Mods)
            self.toolBar.addAction(self.actionEnable_Disable_Mods)
            self.toolBar.setIconSize(QSize(32, 32))
            self.toolBar.addSeparator()

            self.actionAddToToolbar = None
            self.modList = {}

            self.retranslateUi()
            QMetaObject.connectSlotsByName(self.mainWindow)

        except Exception as err:
            self.output(formatUserError(err))


    def retranslateUi(self):
        '''GUI positioning and additional initialziation'''

        self.mainWindow.setWindowTitle(
            TRANSLATE("MainWindow", TITLE))

        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.headerItem().setText(0, TRANSLATE("MainWindow", "Enabled"))
        self.treeWidget.headerItem().setText(1, TRANSLATE("MainWindow", "Mod Name"))
        self.treeWidget.headerItem().setText(2, TRANSLATE("MainWindow", "Priority"))
        self.treeWidget.headerItem().setText(3, TRANSLATE("MainWindow", "Data"))
        self.treeWidget.headerItem().setText(4, TRANSLATE("MainWindow", "DLC"))
        self.treeWidget.headerItem().setText(5, TRANSLATE("MainWindow", "Menu"))
        self.treeWidget.headerItem().setText(6, TRANSLATE("MainWindow", "Var"))
        self.treeWidget.headerItem().setText(7, TRANSLATE("MainWindow", "Hidden"))
        self.treeWidget.headerItem().setText(8, TRANSLATE("MainWindow", "Key"))
        self.treeWidget.headerItem().setText(9, TRANSLATE("MainWindow", "Settings"))
        self.treeWidget.headerItem().setText(10, TRANSLATE("MainWindow", "Size"))
        self.treeWidget.headerItem().setText(11, TRANSLATE("MainWindow", "Date Installed"))

        self.loadOrder.setSortingEnabled(False)
        self.loadOrder.headerItem().setText(0, TRANSLATE("MainWindow", "Load Order"))
        self.loadOrder.headerItem().setText(1, TRANSLATE("MainWindow", "Priority"))

        self.textEdit.setPlaceholderText(TRANSLATE("MainWindow", "Output"))
        self.textEdit.setCursor(QCursor(Qt.ArrowCursor))

        self.pushButton_4.setText(TRANSLATE("MainWindow", "Run Script Merger"))
        self.pushButton_5.setText(TRANSLATE("MainWindow", "Run the Game"))

        self.menuFile.setTitle(TRANSLATE("MainWindow", "Mods"))
        self.menuEdit.setTitle(TRANSLATE("MainWindow", "Edit"))
        self.menuSettings.setTitle(TRANSLATE("MainWindow", "Settings"))
        self.menuSelect_Language.setTitle(TRANSLATE("MainWindow", "Select Language"))
        self.menuConfigure_Settings.setTitle(TRANSLATE("MainWindow", "Configure Settings"))
        self.menuHelp.setTitle(TRANSLATE("MainWindow", "Help"))
        self.toolBar.setWindowTitle(TRANSLATE("MainWindow", "toolBar"))

        self.actionInstall_Mods.setText(TRANSLATE("MainWindow", "Install Mods"))
        self.actionInstall_Mods.setToolTip(
            TRANSLATE("MainWindow", "Install one or more Mods from folders or archives"))
        self.actionInstall_Mods.setShortcut("Ctrl+E")
        self.actionRestore_Columns.setText(
            TRANSLATE("MainWindow", "Restore default column widths"))
        self.actionRestore_Columns.setToolTip(
            TRANSLATE("MainWindow", "Restore default column widths"))
        self.actionUninstall_Mods.setText(
            TRANSLATE("MainWindow", "Uninstall"))
        self.actionUninstall_Mods.setToolTip(
            TRANSLATE("MainWindow", "Uninstall one or more selected Mods"))
        self.actionUninstall_Mods.setShortcut("Del")
        self.actionEnable_Disable_Mods.setText(
            TRANSLATE("MainWindow", "Enable/Disable"))
        self.actionEnable_Disable_Mods.setToolTip(
            TRANSLATE("MainWindow", "Enable or disable selected Mods"))
        self.actionEnable_Disable_Mods.setShortcut("Ctrl+Q")
        self.actionRefresh_Mod_List.setText(
            TRANSLATE("MainWindow", "Refresh Mod List"))
        self.actionRefresh_Mod_List.setShortcut("F5")
        self.actionRefresh_Load_Order.setText(
            TRANSLATE("MainWindow", "Refresh Load Order"))
        self.actionRefresh_Load_Order.setShortcut("F6")
        self.actionSelect_All_Mods.setText(
            TRANSLATE("MainWindow", "Select All Mods"))
        self.actionSelect_All_Mods.setShortcut("Ctrl+A")
        self.actionRun_The_Game.setText(
            TRANSLATE("MainWindow", "Run the Game"))
        self.actionRun_The_Game.setShortcut("Ctrl+R")
        self.actionRun_Script_Merger.setText(
            TRANSLATE("MainWindow", "Run Script Merger"))
        self.actionRun_Script_Merger.setShortcut("Ctrl+S")
        self.actionAbout.setText(
            TRANSLATE("MainWindow", "About"))
        self.actionAbout.setShortcut("F1")
        self.actionMain_Web_Page.setText(
            TRANSLATE("MainWindow", "Main Web Page"))
        self.actionGitHub.setText(
            TRANSLATE("MainWindow", "GitHub"))
        self.actionMain_Web_Page.setShortcut("Ctrl+F1")
        self.actionGitHub.setShortcut("Ctrl+F2")
        self.actionAlert_to_run_Script_Merger.setText(
            TRANSLATE("MainWindow", "Alert to run Script Merger"))
        self.actionChange_Game_Path.setText(
            TRANSLATE("MainWindow", "Change Game Path"))
        self.actionChange_Script_Merger_Path.setText(
            TRANSLATE("MainWindow", "Change Script Merger Path"))
        self.actionClearOutput.setText(
            TRANSLATE("MainWindow", "Clear Output"))
        self.actionRename.setText(
            TRANSLATE("MainWindow", "Rename"))
        self.actionRename.setShortcut("F2")
        self.actionDetails.setShortcut("F3")
        self.actionDetails.setText(
            TRANSLATE("MainWindow", "Details"))
        self.actionOpenFolder.setShortcut("Ctrl+L")
        self.actionOpenFolder.setText(
            TRANSLATE("MainWindow", "Open Folder"))
        self.actionIncreasePriority.setShortcut("Ctrl+Up")
        self.actionIncreasePriority.setText(
            TRANSLATE("MainWindow", "Increase Priority"))
        self.actionDecreasePriority.setShortcut("Ctrl+Down")
        self.actionDecreasePriority.setText(
            TRANSLATE("MainWindow", "Decrease Priority"))
        self.actionSetPriority.setShortcut("Ctrl+P")
        self.actionSetPriority.setText(
            TRANSLATE("MainWindow", "Set Priority"))
        self.actionUnsetPriority.setShortcut("Ctrl+U")
        self.actionUnsetPriority.setText(
            TRANSLATE("MainWindow", "Remove Priority"))

        self.menuEdit.addAction(self.actionDetails)
        self.menuEdit.addAction(self.actionRename)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSetPriority)
        self.menuEdit.addAction(self.actionUnsetPriority)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionIncreasePriority)
        self.menuEdit.addAction(self.actionDecreasePriority)

        self.treeWidget.header().resizeSection(
            0, int(data.config.get('WINDOW', 'section0'))
            if data.config.get('WINDOW', 'section0') else 60)

        def resizeSection(section, size):
            return self.treeWidget.header().resizeSection(section, size)
        def getSection(section):
            return data.config.get('WINDOW', 'section'+str(section))
        def resizeSectionWithDefault(section, default):
            resizeSection(section, int(getSection(section)) if getSection(section) else default)
        resizeSectionWithDefault(1, 200)
        resizeSectionWithDefault(2, 50)
        resizeSectionWithDefault(3, 39)
        resizeSectionWithDefault(4, 39)
        resizeSectionWithDefault(5, 39)
        resizeSectionWithDefault(6, 39)
        resizeSectionWithDefault(7, 45)
        resizeSectionWithDefault(8, 39)
        resizeSectionWithDefault(9, 50)
        resizeSectionWithDefault(10, 45)
        resizeSectionWithDefault(11, 120)

        self.treeWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeWidget.header().setDefaultAlignment(Qt.AlignCenter)
        self.treeWidget.sortByColumn(1, Qt.AscendingOrder)

        self.loadOrder.header().resizeSection(0, 180)
        self.loadOrder.header().resizeSection(1, 40)
        self.loadOrder.header().setDefaultAlignment(Qt.AlignCenter)

        self.actionInstall_Mods.triggered.connect(self.InstallMods)
        self.actionUninstall_Mods.triggered.connect(self.UninstallMods)
        self.actionAbout.triggered.connect(self.About)
        self.actionEnable_Disable_Mods.triggered.connect(self.EnableDisableMods)
        self.actionRefresh_Mod_List.triggered.connect(self.RefreshList)
        self.actionRefresh_Load_Order.triggered.connect(self.RefreshLoadOrder)
        self.actionSelect_All_Mods.triggered.connect(self.SelectAllMods)
        self.actionRun_The_Game.triggered.connect(self.RunTheGame)
        self.actionRun_Script_Merger.triggered.connect(self.RunScriptMerger)
        self.actionMain_Web_Page.triggered.connect(self.MainWebPage)
        self.actionGitHub.triggered.connect(self.OpenGitHub)
        self.actionAlert_to_run_Script_Merger.triggered.connect(self.AlertPopupChanged)
        self.actionChange_Game_Path.triggered.connect(self.ChangeGamePath)
        self.actionChange_Script_Merger_Path.triggered.connect(self.ChangeScriptMergerPath)
        self.actionClearOutput.triggered.connect(self.clear)
        self.actionRename.triggered.connect(self.rename)
        self.actionDetails.triggered.connect(self.details)
        self.actionOpenFolder.triggered.connect(self.openFolder)
        self.actionIncreasePriority.triggered.connect(self.increasePriority)
        self.actionDecreasePriority.triggered.connect(self.decreasePriority)
        self.actionSetPriority.triggered.connect(self.setPriority)
        self.actionUnsetPriority.triggered.connect(self.unsetPriority)
        self.actionRestore_Columns.triggered.connect(self.Restore_Columns)

        self.pushButton_4.clicked.connect(self.RunScriptMerger)
        self.pushButton_5.clicked.connect(self.RunTheGame)

        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.openMenu)

        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolBar.customContextMenuRequested.connect(self.toolbarMenu)

        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.openEditMenu)

        self.treeWidget.itemChanged.connect(self.modToggled)
        self.treeWidget.itemDoubleClicked.connect(self.modDoubleClicked)
        self.treeWidget.header().setStretchLastSection(False)

        self.loadOrder.itemDoubleClicked.connect(self.loadOrderDoubleClicked)


        self.configureSettings()
        self.configureMods()
        self.configureWindow()
        self.configureToolbar()

    def Run(self, option):
        '''Run game or script merger'''
        try:
            os.startfile(data.config.get('PATHS', option))
        except Exception as err:
            self.output(formatUserError(err))

    def Open(self, filename):
        '''Open or run any kind of folder/file or executable'''
        try:
            _, ext = path.splitext(filename)
            if (ext == ".exe" or ext == ".bat"):
                directory, _ = path.split(filename)
                subprocess.Popen(directory, cwd=directory)
            else:
                os.startfile(filename)
        except Exception as err:
            self.output(formatUserError(err))

    # Settings
    def checkGamePath(self, gamepath=""):
        '''Checks to see if given gamepath is correct'''
        if (not gamepath):
            gamepath = data.config.get('PATHS', 'game')
        return path.exists(gamepath) and path.exists(path.dirname(gamepath) + "/../../content")

    def configureWindow(self):
        data.config.set('WINDOW', 'width', "1024")
        data.config.set('WINDOW', 'height', "720")
        data.config.set('WINDOW', 'section0', '60')
        data.config.set('WINDOW', 'section1', '200')
        data.config.set('WINDOW', 'section2', '50')
        data.config.set('WINDOW', 'section3', '39')
        data.config.set('WINDOW', 'section4', '39')
        data.config.set('WINDOW', 'section5', '39')
        data.config.set('WINDOW', 'section6', '39')
        data.config.set('WINDOW', 'section7', '45')
        data.config.set('WINDOW', 'section8', '39')
        data.config.set('WINDOW', 'section9', '50')
        data.config.set('WINDOW', 'section10', '45')
        data.config.set('WINDOW', 'section11', '120')

    def configureSettings(self):
        '''Generates default settings if they are not present'''
        if (not data.config.get('SETTINGS', 'AllowPopups')):
            data.config.set('SETTINGS', 'AllowPopups', str(1))
        if (data.config.get('SETTINGS', 'AllowPopups') == "1"):
            self.actionAlert_to_run_Script_Merger.setChecked(True)
        if (not data.config.get('SETTINGS', 'language')):
            data.config.set('SETTINGS', 'language', 'English.qm')
        self.CheckLanguage()

    def configureMods(self):
        '''Reads all mods data from xml and creates inner mod structure'''
        self.modList = {}
        if (path.exists(data.config.configPath + '/installed.xml')):
            tree = XML.parse(data.config.configPath + '/installed.xml')
            root = tree.getroot()
            for xmlmod in root.findall('mod'):
                mod = Mod()
                mod.populateFromXml(xmlmod)
                self.modList[mod.name] = mod
        self.RefreshList()

    def configureToolbar(self):
        '''Creates and configures toolbar'''
        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.Run('mod'))
        actionTemp.setText('M')
        actionTemp.setIconText(TRANSLATE('MainWindow', 'Mods'))
        actionTemp.setIcon(getIcon("mods.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open Mods folder'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.Run('dlc'))
        actionTemp.setText('D')
        actionTemp.setIconText(TRANSLATE('MainWindow', 'DLC'))
        actionTemp.setIcon(getIcon("dlc.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open DLC folder'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.Run('menu'))
        actionTemp.setText('I')
        actionTemp.setIconText(TRANSLATE('MainWindow', 'Menus'))
        actionTemp.setIcon(getIcon("menu.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open Menus folder'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.Run('settings'))
        actionTemp.setText('S')
        actionTemp.setIconText(TRANSLATE('MainWindow', 'Settings'))
        actionTemp.setIcon(getIcon("settings.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open Settings folder'))
        self.toolBar.addAction(actionTemp)

        self.toolBar.addSeparator()

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: self.Open(data.config.get('PATHS', 'menu') + '/input.xml'))
        actionTemp.setText('Input Xml')
        actionTemp.setIcon(getIcon("xml.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open input.xml file'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: self.Open(data.config.get('PATHS', 'settings') + '/input.settings'))
        actionTemp.setText('Input Settings')
        actionTemp.setIcon(getIcon("input.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open input.settings file'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: self.Open(data.config.get('PATHS', 'settings') + '/user.settings'))
        actionTemp.setText('User Settings')
        actionTemp.setIcon(getIcon("user.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open user.settings file'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: self.Open(data.config.get('PATHS', 'settings') + '/mods.settings'))
        actionTemp.setText('Mods Settings')
        actionTemp.setIcon(getIcon("modset.ico"))
        actionTemp.setToolTip(TRANSLATE("MainWindow", 'Open mods.settings file'))
        self.toolBar.addAction(actionTemp)

        self.toolBar.addSeparator()

        for custom in data.config.getOptions('TOOLBAR'):
            self.addToToolbar(custom)
        self.actionAddToToolbar = QAction(self.mainWindow)
        self.actionAddToToolbar.triggered.connect(self.addToToolbar)
        self.actionAddToToolbar.setText(TRANSLATE("MainWindow", 'Add New..'))

    def openMenu(self, position):
        '''Right click menu on mod list (Left panel)'''
        menu = QMenu()
        menu.addAction(self.actionDetails)
        menu.addSeparator()
        menu.addAction(self.actionSetPriority)
        menu.addAction(self.actionUnsetPriority)
        menu.addSeparator()
        menu.addAction(self.actionOpenFolder)
        menu.addSeparator()
        menu.addAction(self.actionRename)
        menu.addAction(self.actionUninstall_Mods)
        menu.addAction(self.actionEnable_Disable_Mods)
        menu.exec_(self.treeWidget.viewport().mapToGlobal(position))

    def openEditMenu(self, position):
        '''Right click menu on output'''
        menu = QMenu()
        menu.addAction(self.actionClearOutput)
        menu.exec_(self.textEdit.viewport().mapToGlobal(position))

    def toolbarMenu(self, position):
        '''Right click menu on toolbar'''
        menu = QMenu(self.mainWindow)
        menu.addAction(self.actionAddToToolbar)
        rem = QMenu(menu)
        rem.setTitle(TRANSLATE("MainWindow", "Remove.."))
        actions = self.toolBar.actions()[14:]
        for action in actions:
            temp = self.makeTempAction(action)
            rem.addAction(temp)
            del action
        menu.addAction(rem.menuAction())
        menu.exec_(self.toolBar.mapToGlobal(position))

    def RemoveFromToolbar(self, action):
        '''Creates menu for removing actions from toolbar'''
        self.toolBar.removeAction(action)
        data.config.removeOption('TOOLBAR', action.toolTip())

    def addToToolbar(self, selected=""):
        '''Adds custom action to the toolbar selected by user'''
        try:
            if (not selected):
                temp = getFile("", "")
                if (temp):
                    selected = temp[0]

            if (selected):
                fileInfo = QFileInfo(selected)
                iconProvider = QFileIconProvider()
                icon = iconProvider.icon(fileInfo)

                _, file = path.split(selected)
                fl, _ = path.splitext(file)
                actionTemp = QAction(self.mainWindow)
                actionTemp.triggered.connect(lambda: self.Open(selected))
                actionTemp.setText(fl)
                actionTemp.setIcon(icon)
                actionTemp.setToolTip(selected)
                self.toolBar.addAction(actionTemp)
                data.config.setnovalue('TOOLBAR', selected)
        except Exception as err:
            self.output(formatUserError(err))

    def Restore_Columns(self):
        data.config.set('WINDOW', 'section0', '60')
        data.config.set('WINDOW', 'section1', '200')
        data.config.set('WINDOW', 'section2', '50')
        data.config.set('WINDOW', 'section3', '39')
        data.config.set('WINDOW', 'section4', '39')
        data.config.set('WINDOW', 'section5', '39')
        data.config.set('WINDOW', 'section6', '39')
        data.config.set('WINDOW', 'section7', '45')
        data.config.set('WINDOW', 'section8', '39')
        data.config.set('WINDOW', 'section9', '50')
        data.config.set('WINDOW', 'section10', '45')
        data.config.set('WINDOW', 'section11', '120')

        def resizeSection(section, size):
            return self.treeWidget.header().resizeSection(section, size)
        def getSection(section):
            return data.config.get('WINDOW', 'section'+str(section))
        def resizeSectionWithDefault(section, default):
            resizeSection(section, int(getSection(section)) if getSection(section) else default)
        resizeSectionWithDefault(0, 60)
        resizeSectionWithDefault(1, 200)
        resizeSectionWithDefault(2, 50)
        resizeSectionWithDefault(3, 39)
        resizeSectionWithDefault(4, 39)
        resizeSectionWithDefault(5, 39)
        resizeSectionWithDefault(6, 39)
        resizeSectionWithDefault(7, 45)
        resizeSectionWithDefault(8, 39)
        resizeSectionWithDefault(9, 50)
        resizeSectionWithDefault(10, 45)
        resizeSectionWithDefault(11, 120)


    def output(self, appendation):
        '''Prints appendation to the output text field'''
        self.textEdit.append(appendation)

    def clear(self):
        '''Removes all text from output text field'''
        self.textEdit.setText("")

    def rename(self):
        '''Renames selected mod'''
        selected = self.getSelectedMods()
        if (selected):
            if (len(selected) > 1):
                QMessageBox.critical(
                    self,
                    TRANSLATE("MainWindow", "Error"),
                    TRANSLATE("MainWindow", "Select only one mod to rename"))
            else:
                oldname = selected[0]
                newname, ok = QInputDialog.getText(
                    self,
                    TRANSLATE("MainWindow", 'Rename'),
                    TRANSLATE("MainWindow", 'Enter new mod name') + ": ",
                    QLineEdit.Normal, oldname)
                if ok:
                    mod = self.modList[oldname]
                    del self.modList[oldname]
                    mod.name = newname
                    self.modList[newname] = mod
                    self.RefreshList()

    def details(self):
        '''Shows details of the selected mod'''
        selected = self.getSelectedMods()
        if selected:
            for mod in selected:
                __details = DetailsDialog(self, str(self.modList[mod]))
                __details.show()

    def openFolder(self):
        selected = self.getSelectedMods()
        if (selected):
            try:
                for modname in selected:
                    mod = self.modList[modname]
                    for file in mod.files:
                        moddir = data.config.get('PATHS', 'mod') + \
                            ("/~" if not mod.enabled else "/") + file
                        os.startfile(moddir, "explore")
            except Exception as err:
                self.output(formatUserError(err))

    def modToggled(self, item, column):
        '''Triggered when the mod check state is changed.
            Enables or disables the mod based on the current check state'''
        try:
            if item.checkState(column) == Qt.Checked:
                self.modList[item.text(1)].enable()
            elif item.checkState(column) == Qt.Unchecked:
                self.modList[item.text(1)].disable()
            self.RefreshLoadOrder()
        except Exception as err:
            self.output(formatUserError(err))

    def modDoubleClicked(self):
        '''Triggered when double clicked on the mod'''
        self.setPriority()

    def loadOrderDoubleClicked(self, item):
        '''Triggered when double clicked on the mod on the right panel. Sets priority'''
        try:
            selected = item.text(0)
            if (selected[0] == '~'):
                QMessageBox.critical(
                    self,
                    TRANSLATE("MainWindow", "Error"),
                    TRANSLATE("MainWindow", "You cannot set priority to disabled mod") + " ")
                return
            selectedvalue = item.text(1)
            if (selectedvalue):
                value = int(selectedvalue)
            else:
                value = 0
            priority, ok = QInputDialog.getInt(
                self,
                TRANSLATE("MainWindow", "Set Priority"),
                TRANSLATE("MainWindow", "Enter new priority") + ": ", value)
            if (ok):
                data.config.setPriority(str(selected), str(priority))
                data.config.write()
                self.RefreshList()
        except Exception as err:
            self.output(formatUserError(err))

    def increaseLoadOrderPriority(self):
        '''Increases the priority of the selected mods in the load order list'''
        items = self.loadOrder.selectedItems()
        if items:
            item = items[0]
            selected = item.text(0)
            selectedvalue = item.text(1)
            if (selectedvalue):
                value = int(selectedvalue)
            else:
                value = 0
            value = value + 1
            data.config.setPriority(str(selected), str(value))
            item.setText(1, str(value))
            data.config.write()

    def decreaseLoadOrderPriority(self):
        '''Decreases the priority of the selected mods in the load order list'''
        items = self.loadOrder.selectedItems()
        if items:
            item = items[0]
            selected = item.text(0)
            selectedvalue = item.text(1)
            if (selectedvalue):
                value = max(-1, int(selectedvalue) - 1)
                if value < 0:
                    data.config.removeSection(str(selected))
                    item.setText(1, "")
                else:
                    data.config.setPriority(str(selected), str(value))
                    item.setText(0, str(value))
                data.config.write()

    def AlertPopupChanged(self):
        '''Triggered when option to alert popup is changed. Saves the change'''
        if (self.actionAlert_to_run_Script_Merger.isChecked()):
            data.config.set('SETTINGS', 'AllowPopups', "1")
        else:
            data.config.set('SETTINGS', 'AllowPopups', "0")

    def ChangeLanguage(self, language):
        '''Triggered when language is changed. Saves the change and restarts the program'''
        data.config.set('SETTINGS', 'language', str(language))
        button = QMessageBox.question(
            self,
            TRANSLATE("MainWindow", "Change language"),
            TRANSLATE("MainWindow", "You need to restart the program to apply the changes.\n\
                Do you want to restart it now?"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if (button == QMessageBox.Yes):
            restart_program()

    def CheckLanguage(self):
        '''Checks which language is selected, and checks it'''

        language = data.config.get('SETTINGS', 'language')
        for lang in self.menuSelect_Language.actions():
            if (language == lang.text() + ".qm"):
                lang.setChecked(True)
                break

    def setPriority(self):
        '''Sets the priority of the selected mods'''
        try:
            selected = self.getSelectedMods()
            if (selected):
                old_priority = self.modList[selected[0]].priority
                if not old_priority or not old_priority.isdecimal():
                    old_priority = 0
                else:
                    old_priority = int(old_priority)
                priority, ok = QInputDialog.getInt(
                    self,
                    TRANSLATE("MainWindow", "Set Priority"),
                    TRANSLATE("MainWindow", "Enter new priority") + ": ",
                    old_priority)
                if (ok):
                    value = str(priority)
                    for modname in selected:
                        mod = self.modList[modname]
                        if mod.enabled:
                            mod.setPriority(value)
                        else:
                            self.output(TRANSLATE(
                                "MainWindow",
                                "You cannot set priority to disabled mod") + \
                                    " '" + modname + "'")
                    data.config.write()
                    self.RefreshList()
        except Exception as err:
            self.output(formatUserError(err))

    def unsetPriority(self):
        '''Removes priority of the selected mods'''
        selected = self.getSelectedMods()
        if (selected):
            for modname in selected:
                mod = self.modList[modname]
                mod.priority = None
                for modfile in mod.files:
                    data.config.removePriority(modfile)
            data.config.write()
            self.RefreshList()

    def increasePriority(self):
        '''Increases the priority of the selected mods'''
        selected = self.getSelectedMods()
        if (selected):
            for modname in selected:
                mod = self.modList[modname]
                new_priority = int(mod.priority) + 1 \
                    if mod.priority and mod.priority.isdecimal() else 0
                mod.setPriority(str(new_priority))
            data.config.write()
            self.RefreshList()

    def decreasePriority(self):
        '''Decreases the priority of the selected mods'''
        selected = self.getSelectedMods()
        if (selected):
            for modname in selected:
                mod = self.modList[modname]
                new_priority = int(mod.priority) - 1 \
                    if mod.priority and mod.priority.isdecimal() else -1
                if new_priority < 0:
                    mod.priority = None
                    for modfile in mod.files:
                        data.config.removePriority(modfile)
                else:
                    mod.setPriority(str(new_priority))
            data.config.write()
            self.RefreshList()

    def ChangeGamePath(self):
        '''Changes game path'''
        gamepath = str(QFileDialog.getOpenFileName(
            self, TRANSLATE("MainWindow", "Select witcher3.exe"),
            data.config.get('PATHS', 'game'), "*.exe")[0])
        if (self.checkGamePath(gamepath)):
            data.config.set('PATHS', 'game', gamepath)
            self.configurePaths()
            self.RefreshList()
        else:
            QMessageBox.critical(
                self, TRANSLATE("MainWindow", "Selected file not correct"),
                TRANSLATE("MainWindow", "'witcher3.exe' file not selected"),
                QMessageBox.Ok, QMessageBox.Ok)

    def ChangeScriptMergerPath(self):
        '''Changes script merger path'''
        mergerpath = str(
            QFileDialog.getOpenFileName(
                self,
                TRANSLATE("MainWindow", "Select script merger"),
                data.config.get('PATHS', 'scriptmerger'), "*.exe")[0])
        if (mergerpath):
            data.config.set('PATHS', 'scriptmerger', mergerpath)

    def InstallMods(self):
        '''Installs selected mods'''
        self.clear()
        file = getFile(data.config.get('PATHS', 'lastpath'), "*.zip *.rar *.7z")
        self.InstallModFiles(file)

    def InstallModFiles(self, file):
        '''Installs passed list of mods'''
        from src.core.mod import install
        try:
            if file:
                prgrs = 0
                prgrsmax = len(file)
                for mod in file:
                    prgsbefore = 100 * prgrs / prgrsmax
                    prgsafter = 100 * (prgrs + 1) / prgrsmax
                    install(mod, self, prgsbefore, prgsafter)
                    prgrs += 1
                    self.setProgress(100 * prgrs / prgrsmax)
                lastpath, _ = path.split(file[0])
                data.config.set('PATHS', 'lastpath', lastpath)
                self.RefreshList()
                self.AlertRunScriptMerger()
                self.setProgress(0)
            else:
                self.output(TRANSLATE("MainWindow", "Installation canceled"))
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))

    def UninstallMods(self):
        '''Uninstalls selected mods'''
        from src.core.mod import uninstall
        try:
            selected = self.getSelectedMods()
            if (selected):
                clicked = QMessageBox.question(
                    self, TRANSLATE("MainWindow", "Confirm"),
                    TRANSLATE("MainWindow", "Are you sure you want to uninstall ") \
                        + str(len(selected)) + \
                        TRANSLATE("MainWindow", " selected mods"),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if clicked == QMessageBox.Yes:
                    prgrs = 0
                    prgrsmax = len(selected)
                    for modname in selected:
                        try:
                            uninstall(self.modList[modname], self)
                            del self.modList[modname]
                        except Exception as err:
                            self.output(formatUserError(err))
                        prgrs += 1
                        self.setProgress(100 * prgrs / prgrsmax)
                    self.RefreshList()
                    self.setProgress(0)
                    self.AlertRunScriptMerger()
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))

    def RunTheGame(self):
        '''Runs the game'''
        try:
            gamepath = data.config.get('PATHS', 'game')
            directory, _ = path.split(gamepath)
            subprocess.Popen([gamepath], cwd=directory)
        except Exception as err:
            self.output(formatUserError(err))

    def RunScriptMerger(self):
        '''Runs script merger'''
        try:
            scriptmergerpath = data.config.get('PATHS', 'scriptmerger')
            if (scriptmergerpath):
                directory, _ = path.split(scriptmergerpath)
                subprocess.Popen([scriptmergerpath], cwd=directory)
            else:
                self.ChangeScriptMergerPath()
                scriptmergerpath = data.config.get('PATHS', 'scriptmerger')
                if (scriptmergerpath):
                    directory, _ = path.split(scriptmergerpath)
                    subprocess.Popen([scriptmergerpath], cwd=directory)
        except Exception as err:
            self.output(formatUserError(err))

    def About(self):
        '''Opens about window'''
        try:
            QMessageBox.about(
                self,
                TRANSLATE("MainWindow", "About"),
                TRANSLATE(
                    "MainWindow",
                    ""+TITLE+"\n"
                    "Version: "+VERSION+"\n"
                    "Authors: "+(", ".join(AUTHORS))+"\n"
                    "\n"
                    "Written in: Python "+python_version()+"\n"
                    "GUI: PyQt "+QtCore.PYQT_VERSION_STR+"\n"
                    "\n"
                    "Thank you for using "+TITLE+"!"))
        except Exception as err:
            self.output(formatUserError(err))

    def MainWebPage(self):
        '''Opens nexus web page'''
        webbrowser.open(URL_WEB)

    def OpenGitHub(self):
        '''Opens github'''
        webbrowser.open(URL_GIT)

    def SelectAllMods(self):
        '''Selects all mods in the list'''
        self.treeWidget.selectAll()

    def EnableDisableMods(self):
        '''Changes checked state of the selected mods'''
        try:
            selected = self.treeWidget.selectedItems()
            self.setProgress(0)
            prgrs = 0
            prgrsmax = len(selected)
            for item in selected:
                if (item.checkState(0) == Qt.Checked):
                    item.setCheckState(0, Qt.Unchecked)
                else:
                    item.setCheckState(0, Qt.Checked)
                prgrs += 1
                self.setProgress(100 * prgrs / prgrsmax)
            self.RefreshList()
            self.AlertRunScriptMerger()
            self.setProgress(0)
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))

    # Helpers
    def RefreshList(self):
        '''Refreshes mod list'''
        try:
            selected = self.getSelectedMods()
            self.treeWidget.clear()
            moddata = []
            for mod in self.modList.values():
                moddata += mod.files
                modsize = 0
                for modfile in mod.files:
                    modsize += getSize(data.config.get('PATHS', 'mod') + "/" + modfile)
                    modsize += getSize(data.config.get('PATHS', 'mod') + "/~" + modfile)
                userstr = TRANSLATE("MainWindow", 'No')
                if (mod.usersettings):
                    userstr = TRANSLATE("MainWindow", 'Yes')
                self.addToList(
                    mod.enabled,
                    mod.name,
                    mod.getPriority(),
                    len(mod.files),
                    len(mod.dlcs),
                    len(mod.menus),
                    len(mod.xmlkeys),
                    len(mod.hidden),
                    len(mod.inputsettings),
                    userstr,
                    modsize,
                    mod.date
                )
            for item in selected:
                rows = self.treeWidget.findItems(item, Qt.MatchEndsWith, 1)
                if (rows):
                    for row in rows:
                        row.setSelected(True)
            self.RefreshLoadOrder()
            writeAllModsToXMLFile(self.modList, data.config.configPath + '/installed.xml')
        except Exception as err:
            self.output(formatUserError(err))

    def RefreshLoadOrder(self):
        '''Refreshes right panel list - load order'''
        selected = self.getSelectedFiles()
        self.loadOrder.clear()
        dirs = []
        for data_ in os.listdir(data.config.get('PATHS', 'mod')):
            templist = []
            templist.append(data_)
            prt = data.config.getPriority(data_)
            if (prt):
                temp = int(prt)
            else:
                temp = 16777215
            templist.append(temp)
            dirs.append(templist)
        dirs = sorted(dirs, key=getKey)
        for directory in dirs:
            if (isData(directory[0])):
                if (directory[1] == 16777215):
                    res = ''
                else:
                    res = str(directory[1])
                dirlist = [directory[0], res]
                item = CustomTreeWidgetItem(dirlist)
                item.setTextAlignment(1, Qt.AlignCenter)
                self.loadOrder.addTopLevelItem(item)
        for item in selected:
            rows = self.loadOrder.findItems(item.replace("~", ""), Qt.MatchEndsWith, 0)
            if (rows):
                for row in rows:
                    row.setSelected(True)

    def setProgress(self, currentProgress):
        '''Sets the progress to currentProgress'''
        self.progressBar.setProperty("value", currentProgress)

    def addToList(
            self,
            on,
            name,
            prio,
            data_,
            dlc,
            menu,
            keys,
            hidden,
            inputkeys,
            settings,
            size,
            date):
        '''Adds mod data to the list'''
        if (data_ == 0):
            datastr = '-'
        else:
            datastr = str(data_)
        if (dlc == 0):
            dlcstr = '-'
        else:
            dlcstr = str(dlc)
        if (menu == 0):
            menustr = '-'
        else:
            menustr = str(menu)
        if (keys == 0):
            keystr = '-'
        else:
            keystr = str(keys)
        if (inputkeys == 0):
            inkeystr = '-'
        else:
            inkeystr = str(inputkeys)
        if (hidden == 0):
            hiddenstr = '-'
        else:
            hiddenstr = str(hidden)
        size //= 1024
        if (size // 1024 == 0):
            sizestr = str(size) + 'KB'
        else:
            size /= 1024
            sizestr = f"{size:.1f}" + 'MB'
        proplist = [
            '',
            str(name),
            str(prio),
            datastr,
            dlcstr,
            menustr,
            keystr,
            hiddenstr,
            inkeystr,
            str(settings),
            sizestr,
            str(date)]
        item = CustomTreeWidgetItem(proplist)
        item.setTextAlignment(2, Qt.AlignCenter)
        item.setTextAlignment(3, Qt.AlignCenter)
        item.setTextAlignment(4, Qt.AlignCenter)
        item.setTextAlignment(5, Qt.AlignCenter)
        item.setTextAlignment(6, Qt.AlignCenter)
        item.setTextAlignment(7, Qt.AlignCenter)
        item.setTextAlignment(8, Qt.AlignCenter)
        item.setTextAlignment(9, Qt.AlignCenter)
        item.setTextAlignment(10, Qt.AlignRight)
        item.setTextAlignment(11, Qt.AlignCenter)
        if (not '~' in name):
            if (on):
                item.setCheckState(0, Qt.Checked)
            else:
                item.setCheckState(0, Qt.Unchecked)
        self.treeWidget.addTopLevelItem(item)
        return item

    def getSelectedMods(self):
        '''Returns list of mod names of the selected mods'''
        array = []
        getSelected = self.treeWidget.selectedItems()
        if getSelected:
            for selected in getSelected:
                baseNode = selected
                array.append(baseNode.text(1))
        return array

    def getSelectedFiles(self):
        array = []
        getSelected = self.loadOrder.selectedItems()
        if getSelected:
            for selected in getSelected:
                baseNode = selected
                array.append(baseNode.text(0))
        return array

    def addMod(self, name, mod):
        '''Adds mod to the inner mod list structure'''
        self.modList[name] = mod

    def makeTempAction(self, action):
        '''Temp function for bypassing actions with same names problem'''
        temp = QAction(action)
        temp.setText(action.text())
        temp.setIcon(action.icon())
        temp.triggered.connect(lambda: self.RemoveFromToolbar(action))
        return temp

    def makeLangAction(self, ts):
        name, _ = path.splitext(ts)
        action = QAction()
        action.setText(name)
        action.setToolTip(name)
        action.setCheckable(True)
        action.setChecked(False)
        action.triggered.connect(lambda: self.ChangeLanguage(ts))
        return action

    def AlertRunScriptMerger(self):
        '''Shows previous dialog based on settings'''
        if (data.config.get('SETTINGS', 'allowpopups') == "1"):
            res = MessageAlertScript()
            if (res == QMessageBox.Yes):
                self.RunScriptMerger()
