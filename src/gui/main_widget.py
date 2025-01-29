'''Main Widget'''
# pylint: disable=invalid-name,superfluous-parens,wildcard-import,bare-except,broad-except,wildcard-import,unused-wildcard-import,missing-docstring,too-many-lines

from os import path
from sys import platform

from PySide6.QtCore import QFileInfo, QMetaObject, QRect, QSize, Qt, QThread, Signal
from PySide6.QtGui import QCursor, QResizeEvent, QAction, QActionGroup
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileIconProvider,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLineEdit,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from src.core.installer import Installer
from src.core.model import Model
from src.globals import data
from src.globals.constants import *
from src.gui.alerts import (
    MessageAlertIncompleteInstallation,
    MessageAlertScript,
    MessageUnsupportedOSAction,
)
from src.gui.details_dialog import DetailsDialog
from src.gui.tree_widget import CustomTreeWidgetItem
from src.util.syntax import *
from src.util.util import *
from src.gui.themes import get_dark_palette, get_light_palette, get_system_palette


class ModsSettingsWatcher(QThread):
    refresh = Signal(object)

    def __init__(self, *args, **kwargs):
        self.modsEventHandler = PatternMatchingEventHandler(
            patterns=["*mods.settings"],
            ignore_patterns=[],
            ignore_directories=True)
        self.modsEventHandler.on_modified = lambda e: self.refresh.emit(e)
        self.running = False
        self.observer = Observer()
        self.observer.schedule(self.modsEventHandler,
                               path=data.config.settings, recursive=False)
        super().__init__(*args, **kwargs)
        self.observer.start()

    def __drop__(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None


class CustomMainWidget(QWidget):
    '''Main Widget'''

    def __init__(self, parent: QWidget, model: Model):
        super().__init__(parent)

        self.mainWindow = parent
        self.model = model
        self.searchString = ""

        self.modsSettingsWatcher = ModsSettingsWatcher()
        self.modsSettingsWatcher.refresh.connect(
            lambda e: self.refreshLoadOrder())

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

        self.searchWidget = QLineEdit(self.centralwidget)
        self.searchWidget.setObjectName("searchWidget")
        self.searchWidget.setPlaceholderText(translate("MainWindow", "Search"))
        self.verticalLayout_2.addWidget(self.searchWidget)

        self.treeWidget = QTreeWidget(self.centralwidget)
        self.treeWidget.setMinimumSize(QSize(600, 350))
        self.treeWidget.setUniformRowHeights(True)
        self.treeWidget.setAnimated(True)
        self.treeWidget.setHeaderHidden(False)
        self.treeWidget.setColumnCount(8)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setCascadingSectionResizes(True)
        self.treeWidget.header().setHighlightSections(False)
        self.treeWidget.header().setSortIndicatorShown(True)
        self.treeWidget.setSortingEnabled(True)

        self.horizontalSplitter_tree = QSplitter()
        self.horizontalSplitter_tree.setObjectName("horizontalSplitter_tree")
        self.horizontalSplitter_tree.addWidget(self.treeWidget)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.loadOrder = QTreeWidget(self.centralwidget)
        self.loadOrder.setUniformRowHeights(True)
        self.loadOrder.setAnimated(True)
        self.loadOrder.setHeaderHidden(False)
        self.loadOrder.setColumnCount(2)
        self.loadOrder.setObjectName("loadOrder")
        self.loadOrder.setMinimumWidth(200)
        self.loadOrder.setSortingEnabled(False)

        self.horizontalSplitter_tree.addWidget(self.loadOrder)
        self.horizontalSplitter_tree.setCollapsible(0, False)
        self.horizontalSplitter_tree.setCollapsible(1, True)
        self.horizontalSplitter_tree.setStretchFactor(0, 3)
        self.horizontalSplitter_tree.setStretchFactor(1, 1)
        self.verticalLayout_2.addWidget(self.horizontalSplitter_tree)

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
        sizePolicy.setHeightForWidth(
            self.pushButton_4.sizePolicy().hasHeightForWidth())
        self.pushButton_4.setSizePolicy(sizePolicy)
        self.pushButton_4.setMinimumSize(QSize(100, 50))
        self.pushButton_4.setObjectName("pushButton_4")
        self.verticalLayout.addWidget(self.pushButton_4)
        self.pushButton_5 = QPushButton(self.centralwidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton_5.sizePolicy().hasHeightForWidth())
        self.pushButton_5.setSizePolicy(sizePolicy)
        self.pushButton_5.setMinimumSize(QSize(100, 50))
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
        self.menuSelect_Theme = QMenu(self.menuSettings)
        self.menuSelect_Theme.setObjectName("menuSelect_Theme")
        self.mainWindow.setMenuBar(self.menubar)
        self.toolBar = QToolBar(self.mainWindow)
        self.toolBar.setObjectName("toolBar")
        self.mainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.actionInstall_Mods = QAction(self.mainWindow)
        self.actionInstall_Mods.setIcon(getIcon('Add.ico'))
        self.actionInstall_Mods.setIconVisibleInMenu(False)
        self.actionInstall_Mods.setObjectName("actionInstall_Mods")
        self.actionInstall_Mods.setIconText(
            translate('MainWindow', "Add"))
        self.actionRestoreColumns = QAction(self.mainWindow)
        self.actionRestoreColumns.setIconVisibleInMenu(False)
        self.actionRestoreColumns.setObjectName("actionRestoreColumns")
        self.actionUninstall_Mods = QAction(self.mainWindow)
        self.actionUninstall_Mods.setIcon(getIcon('rem.ico'))
        self.actionUninstall_Mods.setIconVisibleInMenu(False)
        self.actionUninstall_Mods.setObjectName("actionUninstall_Mods")
        self.actionUninstall_Mods.setIconText(
            translate('MainWindow', "Remove"))
        self.actionEnable_Disable_Mods = QAction(self.mainWindow)
        self.actionEnable_Disable_Mods.setIcon(getIcon('check.ico'))
        self.actionEnable_Disable_Mods.setIconVisibleInMenu(False)
        self.actionEnable_Disable_Mods.setObjectName(
            "actionEnable_Disable_Mods")
        self.actionEnable_Disable_Mods.setIconText(
            translate('MainWindow', "Toggle"))
        self.actionReinstall_Mods = QAction(self.mainWindow)
        self.actionReinstall_Mods.setObjectName("actionReinstall_Mods")
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
        self.actionAlert_to_run_Script_Merger.setObjectName(
            "actionAlert_to_run_Script_Merger")
        self.languageActionGroup = QActionGroup(self.mainWindow)
        for lang in os.listdir(getProgramRootFolder() + '/translations/'):
            temp = self.makeLangAction(lang)
            self.languageActionGroup.addAction(temp)
            self.menuSelect_Language.addAction(temp)
        self.actionChange_Game_Path = QAction(self.mainWindow)
        self.actionChange_Game_Path.setObjectName("actionChange_Game_Path")
        self.actionChange_Script_Merger_Path = QAction(self.mainWindow)
        self.actionChange_Script_Merger_Path.setObjectName(
            "actionChange_Script_Merger_Path")
        self.actionClearOutput = QAction(self.mainWindow)
        self.actionClearOutput.setObjectName("actionClearOutput")

        self.menuFile.addAction(self.actionInstall_Mods)
        self.menuFile.addAction(self.actionUninstall_Mods)
        self.menuFile.addAction(self.actionEnable_Disable_Mods)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpenFolder)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionReinstall_Mods)
        self.menuFile.addAction(self.actionRefresh_Mod_List)
        self.menuFile.addAction(self.actionRefresh_Load_Order)
        self.menuFile.addAction(self.actionSelect_All_Mods)

        self.menuConfigure_Settings.addAction(self.actionChange_Game_Path)
        self.menuConfigure_Settings.addAction(
            self.actionChange_Script_Merger_Path)
        self.menuConfigure_Settings.addSeparator()
        self.menuConfigure_Settings.addAction(self.actionRestoreColumns)
        self.menuConfigure_Settings.addSeparator()
        self.menuConfigure_Settings.addAction(
            self.actionAlert_to_run_Script_Merger)
        self.menuConfigure_Settings.addSeparator()
        self.menuSettings.addAction(self.menuConfigure_Settings.menuAction())
        self.menuSettings.addAction(self.menuSelect_Language.menuAction())
        self.menuSelect_Theme.setTitle(translate("MainWindow", "Select Theme"))
        self.menuSettings.addAction(self.menuSelect_Theme.menuAction())

        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionMain_Web_Page)
        self.menuHelp.addAction(self.actionGitHub)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.actionAddToToolbar = None

        self.themeActionGroup = QActionGroup(self.mainWindow)
        for theme in ['Follow System', 'Light', 'Dark']:
            action = QAction(theme, self.mainWindow, checkable=True)
            action.triggered.connect(lambda _, t=theme: self.changeTheme(t))
            self.themeActionGroup.addAction(action)
            self.menuSelect_Theme.addAction(action)

        self.translateUi()
        self.configureUi()
        self.configureToolbar()
        self.checkLanguage()
        self.refreshList()

        QMetaObject.connectSlotsByName(self.mainWindow)

        self.mainWindow.resizeEvent = lambda e: self.onResize()  # type: ignore
        self.loadOrder.header().sectionResized.connect(lambda: self.onResize())
        self.treeWidget.header().sectionResized.connect(lambda: self.onResize())

    @debounce(200)
    def onResize(self):
        data.config.saveWindowSettings(self, self.mainWindow)

    def resizeEvent(self, event: QResizeEvent):
        self.onResize()

    def translateUi(self):
        self.mainWindow.setWindowTitle(
            translate("MainWindow", TITLE))

        self.treeWidget.headerItem().setText(0, translate("MainWindow", "Enabled"))
        self.treeWidget.headerItem().setText(1, translate("MainWindow", "Mod Name"))
        self.treeWidget.headerItem().setText(2, translate("MainWindow", "Priority"))
        self.treeWidget.headerItem().setText(3, translate("MainWindow", "Data"))
        self.treeWidget.headerItem().setText(4, translate("MainWindow", "DLC"))
        self.treeWidget.headerItem().setText(5, translate("MainWindow", "Menu"))
        self.treeWidget.headerItem().setText(6, translate("MainWindow", "Var"))
        self.treeWidget.headerItem().setText(7, translate("MainWindow", "Hidden"))
        self.treeWidget.headerItem().setText(8, translate("MainWindow", "Key"))
        self.treeWidget.headerItem().setText(9, translate("MainWindow", "Settings"))
        self.treeWidget.headerItem().setText(10, translate("MainWindow", "Size"))
        self.treeWidget.headerItem().setText(
            11, translate("MainWindow", "Date Installed"))

        self.loadOrder.headerItem().setText(0, translate("MainWindow", "Load Order"))
        self.loadOrder.headerItem().setText(1, translate("MainWindow", "Priority"))

        self.textEdit.setPlaceholderText(translate("MainWindow", "Output"))
        self.textEdit.setCursor(QCursor(Qt.ArrowCursor))

        self.pushButton_4.setText(translate("MainWindow", "Run Script Merger"))
        self.pushButton_5.setText(
            translate("MainWindow", "Run the Game") + " (" + data.config.graphicsapi + ")")

        self.menuFile.setTitle(translate("MainWindow", "Mods"))
        self.menuEdit.setTitle(translate("MainWindow", "Edit"))
        self.menuSettings.setTitle(translate("MainWindow", "Settings"))
        self.menuSelect_Language.setTitle(
            translate("MainWindow", "Select Language"))
        self.menuConfigure_Settings.setTitle(
            translate("MainWindow", "Configure Settings"))
        self.menuHelp.setTitle(translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(translate("MainWindow", "toolBar"))

        self.actionInstall_Mods.setText(
            translate("MainWindow", "Install Mods"))
        self.actionInstall_Mods.setToolTip(
            translate("MainWindow", "Install one or more Mods from folders or archives"))
        self.actionInstall_Mods.setShortcut("Ctrl+E")
        self.actionRestoreColumns.setText(
            translate("MainWindow", "Restore default column widths"))
        self.actionRestoreColumns.setToolTip(
            translate("MainWindow", "Restore default column widths"))
        self.actionUninstall_Mods.setText(
            translate("MainWindow", "Uninstall"))
        self.actionUninstall_Mods.setToolTip(
            translate("MainWindow", "Uninstall one or more selected Mods"))
        self.actionUninstall_Mods.setShortcut("Del")
        self.actionEnable_Disable_Mods.setText(
            translate("MainWindow", "Enable/Disable"))
        self.actionEnable_Disable_Mods.setToolTip(
            translate("MainWindow", "Enable or disable selected Mods"))
        self.actionEnable_Disable_Mods.setShortcut("Ctrl+Q")
        self.actionRefresh_Mod_List.setText(
            translate("MainWindow", "Refresh Mod List"))
        self.actionRefresh_Mod_List.setShortcut("F5")
        self.actionReinstall_Mods.setText(
            translate("MainWindow", "Reinstall"))
        self.actionRefresh_Load_Order.setText(
            translate("MainWindow", "Refresh Load Order"))
        self.actionRefresh_Load_Order.setShortcut("F6")
        self.actionSelect_All_Mods.setText(
            translate("MainWindow", "Select All Mods"))
        self.actionSelect_All_Mods.setShortcut("Ctrl+A")
        self.actionRun_The_Game.setText(
            translate("MainWindow", "Run the Game"))
        self.actionRun_The_Game.setShortcut("Ctrl+R")
        self.actionRun_Script_Merger.setText(
            translate("MainWindow", "Run Script Merger"))
        self.actionRun_Script_Merger.setShortcut("Ctrl+S")
        self.actionAbout.setText(
            translate("MainWindow", "About"))
        self.actionAbout.setShortcut("F1")
        self.actionMain_Web_Page.setText(
            translate("MainWindow", "Main Web Page"))
        self.actionGitHub.setText(
            translate("MainWindow", "GitHub"))
        self.actionMain_Web_Page.setShortcut("Ctrl+F1")
        self.actionGitHub.setShortcut("Ctrl+F2")
        self.actionAlert_to_run_Script_Merger.setText(
            translate("MainWindow", "Alert to run Script Merger"))
        self.actionChange_Game_Path.setText(
            translate("MainWindow", "Change Game Path"))
        self.actionChange_Script_Merger_Path.setText(
            translate("MainWindow", "Change Script Merger Path"))
        self.actionClearOutput.setText(
            translate("MainWindow", "Clear Output"))
        self.actionRename.setText(
            translate("MainWindow", "Rename"))
        self.actionRename.setShortcut("F2")
        self.actionDetails.setShortcut("F3")
        self.actionDetails.setText(
            translate("MainWindow", "Details"))
        self.actionOpenFolder.setShortcut("Ctrl+L")
        self.actionOpenFolder.setText(
            translate("MainWindow", "Open Folder"))
        self.actionIncreasePriority.setShortcut("Ctrl+Up")
        self.actionIncreasePriority.setText(
            translate("MainWindow", "Increase Priority"))
        self.actionDecreasePriority.setShortcut("Ctrl+Down")
        self.actionDecreasePriority.setText(
            translate("MainWindow", "Decrease Priority"))
        self.actionSetPriority.setShortcut("Ctrl+P")
        self.actionSetPriority.setText(
            translate("MainWindow", "Set Priority"))
        self.actionUnsetPriority.setShortcut("Ctrl+U")
        self.actionUnsetPriority.setText(
            translate("MainWindow", "Remove Priority"))

        self.menuEdit.addAction(self.actionDetails)
        self.menuEdit.addAction(self.actionRename)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSetPriority)
        self.menuEdit.addAction(self.actionUnsetPriority)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionIncreasePriority)
        self.menuEdit.addAction(self.actionDecreasePriority)

    def configureUi(self):
        for i in range(0, self.treeWidget.header().count()):
            if not data.config.getWindowSection(i):
                data.config.setDefaultWindow()
                break

        self.treeWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeWidget.header().setDefaultAlignment(Qt.AlignCenter)
        self.treeWidget.sortByColumn(1, Qt.AscendingOrder)

        self.loadOrder.header().setDefaultAlignment(Qt.AlignCenter)
        self.loadOrder.header().setStretchLastSection(False)
        self.loadOrder.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.loadOrder.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.resizeColumns()

        self.actionInstall_Mods.triggered.connect(self.installMods)
        self.actionUninstall_Mods.triggered.connect(self.uninstallMods)
        self.actionReinstall_Mods.triggered.connect(self.reinstallMods)
        self.actionAbout.triggered.connect(showAboutWindow)
        self.actionEnable_Disable_Mods.triggered.connect(
            self.enableDisableMods)
        self.actionRefresh_Mod_List.triggered.connect(
            lambda e: self.refreshList())
        self.actionRefresh_Load_Order.triggered.connect(
            lambda e: self.refreshLoadOrder())
        self.actionSelect_All_Mods.triggered.connect(self.selectAllMods)
        self.actionRun_The_Game.triggered.connect(self.runTheGame)
        self.actionRun_Script_Merger.triggered.connect(self.runScriptMerger)
        self.actionMain_Web_Page.triggered.connect(lambda: openUrl(URL_WEB))
        self.actionGitHub.triggered.connect(lambda: openUrl(URL_GIT))
        self.actionAlert_to_run_Script_Merger.triggered.connect(
            self.alertPopupChanged)
        self.actionChange_Game_Path.triggered.connect(self.changeGamePath)
        self.actionChange_Script_Merger_Path.triggered.connect(
            self.changeScriptMergerPath)
        self.actionClearOutput.triggered.connect(self.clear)
        self.actionRename.triggered.connect(self.rename)
        self.actionDetails.triggered.connect(self.details)
        self.actionOpenFolder.triggered.connect(self.openFolder)
        self.actionIncreasePriority.triggered.connect(self.increasePriority)
        self.actionDecreasePriority.triggered.connect(self.decreasePriority)
        self.actionSetPriority.triggered.connect(self.setPriority)
        self.actionUnsetPriority.triggered.connect(self.unsetPriority)
        self.actionRestoreColumns.triggered.connect(self.restoreColumns)

        self.pushButton_4.clicked.connect(self.runScriptMerger)
        self.pushButton_5.clicked.connect(self.runTheGame)

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

        self.actionAlert_to_run_Script_Merger.setChecked(
            data.config.allowpopups == '1')

        self.searchWidget.textChanged.connect(self.setSearchString)

    def openByConfigKey(self, option):
        '''Open or run any kind of folder/file or executable by configuration key'''
        openFile(getattr(data.config, option))

    def configureToolbar(self):
        '''Creates and configures toolbar'''
        self.toolBar.clear()

        self.toolBar.addAction(self.actionInstall_Mods)
        self.toolBar.addAction(self.actionUninstall_Mods)
        self.toolBar.addAction(self.actionEnable_Disable_Mods)
        self.toolBar.setIconSize(QSize(32, 32))
        self.toolBar.addSeparator()

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.openByConfigKey('mods'))
        actionTemp.setText('M')
        actionTemp.setIconText(translate('MainWindow', 'Mods'))
        actionTemp.setIcon(getIcon("mods.ico"))
        actionTemp.setToolTip(translate("MainWindow", 'Open Mods folder'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.openByConfigKey('dlc'))
        actionTemp.setText('D')
        actionTemp.setIconText(translate('MainWindow', 'DLC'))
        actionTemp.setIcon(getIcon("dlc.ico"))
        actionTemp.setToolTip(translate("MainWindow", 'Open DLC folder'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.openByConfigKey('menu'))
        actionTemp.setText('I')
        actionTemp.setIconText(translate('MainWindow', 'Menus'))
        actionTemp.setIcon(getIcon("menu.ico"))
        actionTemp.setToolTip(translate("MainWindow", 'Open Menus folder'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(lambda: self.openByConfigKey('settings'))
        actionTemp.setText('S')
        actionTemp.setIconText(translate('MainWindow', 'Settings'))
        actionTemp.setIcon(getIcon("settings.ico"))
        actionTemp.setToolTip(translate("MainWindow", 'Open Settings folder'))
        self.toolBar.addAction(actionTemp)

        self.toolBar.addSeparator()

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: openFile(data.config.menu + '/input.xml'))
        actionTemp.setText(translate("MainWindow", 'Input Xml'))
        actionTemp.setIcon(getIcon("xml.ico"))
        actionTemp.setToolTip(translate("MainWindow", 'Open input.xml file'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: openFile(data.config.settings + '/input.settings'))
        actionTemp.setText(translate("MainWindow", 'Input Settings'))
        actionTemp.setIcon(getIcon("input.ico"))
        actionTemp.setToolTip(
            translate("MainWindow", 'Open input.settings file'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: openFile(data.config.settings + "/" + data.config.usersettings))
        actionTemp.setText(translate("MainWindow", 'User Settings'))
        actionTemp.setIcon(getIcon("user.ico"))
        actionTemp.setToolTip(
            translate("MainWindow", 'Open user.settings file'))
        self.toolBar.addAction(actionTemp)

        actionTemp = QAction(self.mainWindow)
        actionTemp.triggered.connect(
            lambda: openFile(data.config.settings + '/mods.settings'))
        actionTemp.setText(translate("MainWindow", 'Mods Settings'))
        actionTemp.setIcon(getIcon("modset.ico"))
        actionTemp.setToolTip(
            translate("MainWindow", 'Open mods.settings file'))
        self.toolBar.addAction(actionTemp)

        self.toolBar.addSeparator()

        for custom in data.config.getOptions('TOOLBAR'):
            self.addToToolbar(custom)
        self.actionAddToToolbar = QAction(self.mainWindow)
        self.actionAddToToolbar.triggered.connect(self.addToToolbar)
        self.actionAddToToolbar.setText(translate("MainWindow", 'Add New..'))

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
        menu.addAction(self.actionReinstall_Mods)
        menu.addAction(self.actionUninstall_Mods)
        menu.addAction(self.actionEnable_Disable_Mods)
        menu.exec(self.treeWidget.viewport().mapToGlobal(position))

    def openEditMenu(self, position):
        '''Right click menu on output'''
        menu = QMenu()
        menu.addAction(self.actionClearOutput)
        menu.exec(self.textEdit.viewport().mapToGlobal(position))

    def toolbarMenu(self, position):
        '''Right click menu on toolbar'''
        menu = QMenu(self.mainWindow)
        menu.addAction(self.actionAddToToolbar)
        rem = QMenu(menu)
        rem.setTitle(translate("MainWindow", "Remove.."))
        actions = self.toolBar.actions()[14:]
        for action in actions:
            temp = self.makeTempAction(action)
            rem.addAction(temp)
            del action
        menu.addAction(rem.menuAction())
        menu.exec(self.toolBar.mapToGlobal(position))

    def removeFromToolbar(self, action):
        '''Creates menu for removing actions from toolbar'''
        self.toolBar.removeAction(action)
        data.config.removeOption('TOOLBAR', action.toolTip())

    def addToToolbar(self, selected=""):
        '''Adds custom action to the toolbar selected by user'''
        try:
            if (not selected):
                temp = getFile(self)
                if (temp):
                    selected = temp[0]
            if (selected):
                fileInfo = QFileInfo(selected)
                iconProvider = QFileIconProvider()
                icon = iconProvider.icon(fileInfo)

                _, file = path.split(selected)
                fl, _ = path.splitext(file)
                actionTemp = QAction(self.mainWindow)
                actionTemp.triggered.connect(lambda: openFile(selected))
                actionTemp.setText(fl)
                actionTemp.setIcon(icon)
                actionTemp.setToolTip(selected)
                self.toolBar.addAction(actionTemp)
                data.config.setOption('TOOLBAR', selected)
        except Exception as err:
            self.output(formatUserError(err))

    def restoreColumns(self):
        data.config.setDefaultWindow()
        self.resizeColumns()

    def resizeColumns(self):
        for i in range(0, self.treeWidget.header().count()):
            self.treeWidget.header().resizeSection(i, data.config.getWindowSection(i) or 60)
        for i in range(0, self.loadOrder.header().count() + 1):
            size = data.config.getWindowSection(i, 'lo')
            if size:
                self.loadOrder.header().resizeSection(i, size)
        try:
            hsplit0 = data.config.get('WINDOW', 'hsplit0')
            hsplit1 = data.config.get('WINDOW', 'hsplit1')
            if hsplit0 and hsplit1:
                self.horizontalSplitter_tree.setSizes(
                    [int(hsplit0), int(hsplit1)])
        except Exception as e:
            print(f"couldn't restore split: {e}")

    def output(self, appendation):
        '''Prints appendation to the output text field'''
        self.textEdit.append(appendation)

    def clear(self):
        '''Removes all text from output text field'''
        self.textEdit.setText("")

    def rename(self):
        '''Renames selected mod'''
        selected = self.getSelectedMods()
        if selected:
            try:
                renamed = 0
                for oldname in selected:
                    newname, ok = QInputDialog.getText(
                        None,
                        translate("MainWindow", 'Rename') + " " + oldname,
                        translate("MainWindow", 'Enter new mod name') + ": ",
                        QLineEdit.Normal, oldname)
                    if ok:
                        self.model.rename(oldname, newname)
                        renamed += 1
                if renamed:
                    self.refreshList()
            except Exception as err:
                self.output(formatUserError(err))

    def details(self):
        '''Shows details of the selected mods'''
        selected = self.getSelectedMods()
        if selected:
            try:
                for modname in selected:
                    details = DetailsDialog(self, self.model.get(modname))
                    details.show()
            except Exception as err:
                self.output(formatUserError(err))

    def openFolder(self):
        '''Open folders of the selected mods'''
        selected = self.getSelectedMods()
        if selected:
            try:
                for modname in selected:
                    self.model.explore(modname)
            except Exception as err:
                self.output(formatUserError(err))

    def modToggled(self, item, column):
        '''Triggered when the mod check state is changed.
            Enables or disables the mod based on the current check state'''
        try:
            if item.checkState(column) == Qt.Checked:
                incomplete = self.model.get(item.text(1)).enable()
                if incomplete:
                    for i in incomplete:
                        self.output(translate("MainWindow", "Note: Additions to ") +
                                    i + translate("MainWindow", " could not be automatically installed."))
            elif item.checkState(column) == Qt.Unchecked:
                self.model.get(item.text(1)).disable()
            self.model.write()
            self.refreshLoadOrder()
            self.alertRunScriptMerger()
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
                    translate("MainWindow", "Error"),
                    translate("MainWindow", "You cannot set priority to disabled mod") + " ")
                return
            selectedvalue = item.text(1)
            if (selectedvalue):
                value = int(selectedvalue)
            else:
                value = 0
            priority, ok = QInputDialog.getInt(
                self,
                translate("MainWindow", "Set Priority"),
                translate("MainWindow", "Enter new priority") + ": ", value)
            if (ok):
                data.config.setPriority(str(selected), str(priority))
                data.config.write_priority()
                self.refreshList()
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
            data.config.write_priority()

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
                data.config.write_priority()

    def alertPopupChanged(self):
        '''Triggered when option to alert popup is changed. Saves the change'''
        if (self.actionAlert_to_run_Script_Merger.isChecked()):
            data.config.allowpopups = '1'
        else:
            data.config.allowpopups = '0'

    def changeLanguage(self, language):
        '''Triggered when language is changed. Saves the change and restarts the program'''
        data.config.language = str(language)
        button = QMessageBox.question(
            self,
            translate("MainWindow", "Change language"),
            translate("MainWindow", "You need to restart the program to apply the changes.")+"\n" +
            translate("MainWindow", "Do you want to restart it now?"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if (button == QMessageBox.Yes):
            restartProgram()

    def checkLanguage(self):
        '''Checks which language is selected, and checks it'''
        language = data.config.language
        for lang in self.menuSelect_Language.actions():
            if (language == lang.text() + ".qm"):
                lang.setChecked(True)
                break

    def setPriority(self):
        '''Sets the priority of the selected mods'''
        try:
            selected = self.getSelectedMods()
            if selected:
                old_priority = self.model.get(selected[0]).priority
                if not old_priority or not old_priority.isdecimal():
                    old_priority = 0
                else:
                    old_priority = int(old_priority)
                priority, ok = QInputDialog.getInt(
                    self,
                    translate("MainWindow", "Set Priority"),
                    translate("MainWindow", "Enter new priority: "),
                    old_priority)
                if not ok:
                    return
                for modname in selected:
                    mod = self.model.get(modname)
                    if mod.enabled:
                        mod.priority = priority
                    else:
                        self.output(translate(
                            "MainWindow",
                            "You cannot set priority to disabled mod") +
                            " '" + modname + "'")
                data.config.write_priority()
                self.refreshList()
        except Exception as err:
            self.output(formatUserError(err))

    def unsetPriority(self):
        '''Removes priority of the selected mods'''
        selected = self.getSelectedMods()
        if selected:
            for modname in selected:
                self.model.get(modname).priority = None
            data.config.write_priority()
            self.refreshList()

    def increasePriority(self):
        '''Increases the priority of the selected mods'''
        selected = self.getSelectedMods()
        if selected:
            for modname in selected:
                self.model.get(modname).increasePriority()
            data.config.write_priority()
            self.refreshList()

    def decreasePriority(self):
        '''Decreases the priority of the selected mods'''
        selected = self.getSelectedMods()
        if selected:
            for modname in selected:
                self.model.get(modname).decreasePriority()
            data.config.write_priority()
            self.refreshList()

    def changeGamePath(self):
        '''Changes game path'''
        if reconfigureGamePath():
            self.refreshList()
            self.translateUi()
            self.configureToolbar()

    def changeScriptMergerPath(self):
        '''Changes script merger path'''
        reconfigureScriptMergerPath()

    def installMods(self):
        '''Installs selected mods'''
        self.clear()
        file = getFile(self, data.config.lastpath, "*.zip *.rar *.7z")
        self.installModFiles(file)

    def installModFiles(self, file):
        '''Installs passed list of mods'''
        try:
            successCount = 0
            errorCount = 0
            incompleteCount = 0
            if file:
                progress = 0
                progressMax = len(file)
                installer = Installer(self.model, output=self.output)
                for mod in file:
                    progressStart = 100 * progress / progressMax
                    progressEnd = 100 * (progress + 1) / progressMax
                    progressCur = progressEnd - progressStart
                    # pylint: disable=cell-var-from-loop
                    installer.progress = lambda p: \
                        self.setProgress(progressStart + progressCur * p)
                    result, count, incomplete = installer.installMod(mod)
                    if result:
                        successCount += count
                    else:
                        errorCount += 1
                    if incomplete:
                        incompleteCount += 1
                    progress += 1
                    self.setProgress(100 * progress / progressMax)
                lastpath, _ = path.split(file[0])
                data.config.lastpath = lastpath
                self.refreshList()
                if incompleteCount:
                    MessageAlertIncompleteInstallation()
                if successCount:
                    self.alertRunScriptMerger()
                self.setProgress(0)
            else:
                self.output(translate("MainWindow", "Installation canceled"))
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))
            errorCount += 1
        self.output(
            '> ' +
            translate("MainWindow", "Installed") +
            f' {successCount} ' +
            translate("MainWindow", "mods or dlcs") +
            f' ({errorCount} ' +
            translate("MainWindow", "errors")+')' +
            (f' ({incompleteCount} ' + translate("MainWindow", "incomplete") + ')' if incompleteCount else ''))

    def uninstallMods(self):
        '''Uninstalls selected mods'''
        try:
            selected = self.getSelectedMods()
            if selected:
                errors = 0
                clicked = QMessageBox.question(
                    self, translate("MainWindow", "Confirm"),
                    translate("MainWindow",
                              "Are you sure you want to uninstall ")
                    + str(len(selected)) +
                    translate("MainWindow", " selected mods?"),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if clicked == QMessageBox.Yes:
                    progress = 0
                    progressMax = len(selected)
                    installer = Installer(self.model, output=self.output)
                    for modname in selected:
                        success = installer.uninstallMod(
                            self.model.get(modname))
                        if not success:
                            errors += 1
                        progress += 1
                        self.setProgress(100 * progress / progressMax)
                    self.refreshList()
                    self.setProgress(0)
                    if errors:
                        self.output(
                            translate("MainWindow", "Failed to uninstall ") + str(errors) + " " + translate("MainWindow", "mods"))
                    else:
                        self.alertRunScriptMerger()
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))

    def reinstallMods(self):
        '''Reinstalls selected mods'''
        try:
            selected = self.getSelectedMods()
            if selected:
                errors = 0
                incompleteCount = 0
                clicked = QMessageBox.question(
                    self, translate("MainWindow", "Confirm"),
                    translate("MainWindow",
                              "Are you sure you want to reinstall ")
                    + str(len(selected)) +
                    translate("MainWindow", " selected mods?") + "\n\n" +
                    translate("MainWindow", "This will override the mods settings with " +
                              "their defaults."),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if clicked == QMessageBox.Yes:
                    self.setProgress(20)
                    installer = Installer(self.model, output=self.output)
                    for modname in selected:
                        success, incomplete = installer.reinstallMod(
                            self.model.get(modname))
                        if not success:
                            errors += 1
                        if incomplete:
                            incompleteCount += 1
                    self.setProgress(100)
                    self.refreshList()
                    self.setProgress(0)
                    if incompleteCount:
                        MessageAlertIncompleteInstallation()
                    if errors:
                        self.output(
                            translate("MainWindow", "Failed to reinstall ") + str(errors) + " " + translate("MainWindow", "mods"))
                    if errors < len(selected):
                        self.alertRunScriptMerger()
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))

    def runTheGame(self):
        '''Runs the game'''
        try:
            if data.config.gamelaunchcommand:
                subprocess.Popen(
                    data.config.gamelaunchcommand)
            else:
                gamepath = data.config.gameexe
                directory, _ = path.split(gamepath)
                if platform == "win32" or platform == "cygwin":
                    subprocess.Popen([gamepath], cwd=directory)
                else:
                    MessageUnsupportedOSAction(
                        translate("MainWindow", "Please run the game through Steam."))
        except Exception as err:
            self.output(formatUserError(err))

    def runScriptMerger(self):
        '''Runs script merger'''
        try:
            scriptmergerpath = data.config.scriptmerger
            if not scriptmergerpath:
                self.changeScriptMergerPath()
                scriptmergerpath = data.config.scriptmerger
            directory, _ = path.split(scriptmergerpath)
            if platform == "win32" or platform == "cygwin":
                subprocess.Popen([scriptmergerpath], cwd=directory)
            elif platform == "linux" or platform == "darwin":
                if data.config.mergerlaunchcommand:
                    subprocess.Popen(
                        data.config.mergerlaunchcommand, cwd=directory, shell=True)
                else:
                    subprocess.Popen(["wine", scriptmergerpath], cwd=directory)
            else:
                MessageUnsupportedOSAction("")
        except Exception as err:
            self.output(formatUserError(err))

    def selectAllMods(self):
        '''Selects all mods in the list'''
        self.treeWidget.selectAll()

    def enableDisableMods(self):
        '''Changes checked state of the selected mods'''
        try:
            selected = self.treeWidget.selectedItems()
            if not selected:
                return
            self.setProgress(0)
            progress = 0
            progressMax = len(selected)
            for item in selected:
                if (item.checkState(0) == Qt.Checked):
                    item.setCheckState(0, Qt.Unchecked)
                else:
                    item.setCheckState(0, Qt.Checked)
                progress += 1
                self.setProgress(100 * progress / progressMax)
            self.refreshList()
            self.alertRunScriptMerger()
            self.setProgress(0)
        except Exception as err:
            self.setProgress(0)
            self.output(formatUserError(err))

    def setSearchString(self, searchString):
        self.searchString = searchString
        self.refreshList()

    # Helpers

    @throttle(200)
    def refreshList(self):
        '''Refreshes mod list'''
        try:
            selected = self.getSelectedMods()
            self.treeWidget.clear()
            moddata = []
            for mod in self.model.all():
                if len(self.searchString) > 0:
                    if self.searchString.lower() not in mod.name.lower():
                        continue
                moddata += mod.files
                modsize = 0
                for modfile in mod.files:
                    modsize += getSize(data.config.mods + "/" + modfile)
                    modsize += getSize(data.config.mods + "/~" + modfile)
                userstr = translate("MainWindow", 'No')
                if (mod.usersettings):
                    userstr = translate("MainWindow", 'Yes')
                self.addToList(
                    mod.enabled,
                    mod.name,
                    mod.priority,
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
            self.refreshLoadOrder()
            self.model.write()
        except Exception as err:
            self.output(
                translate("MainWindow", "Couldn't refresh list: ") + f"{formatUserError(err)}")
            return err
        return None

    @debounce(100)
    def refreshLoadOrder(self):
        '''Refreshes right panel list - load order'''
        try:
            selected = self.getSelectedFiles()
            self.loadOrder.clear()
            data.config.readPriority()
            dirs = []
            for data_ in os.listdir(data.config.mods):
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
                rows = self.loadOrder.findItems(
                    item.replace("~", ""), Qt.MatchEndsWith, 0)
                if (rows):
                    for row in rows:
                        row.setSelected(True)
        except Exception as err:
            self.output(
                translate("MainWindow", "Couldn't read or refresh load order: ") + f"{formatUserError(err)}")
            return err
        return None

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
        if ('~' not in name):
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

    def makeTempAction(self, action):
        '''Temp function for bypassing actions with same names problem'''
        temp = QAction(action)
        temp.setText(action.text())
        temp.setIcon(action.icon())
        temp.triggered.connect(lambda: self.removeFromToolbar(action))
        return temp

    def makeLangAction(self, ts):
        name, _ = path.splitext(ts)
        action = QAction()
        action.setText(name)
        action.setToolTip(name)
        action.setCheckable(True)
        action.setChecked(False)
        action.triggered.connect(lambda: self.changeLanguage(ts))
        return action

    @throttle(2000)
    def alertRunScriptMerger(self):
        '''Shows previous dialog based on settings'''
        if (data.config.allowpopups == "1"):
            res = MessageAlertScript()
            if (res == QMessageBox.Yes):
                self.runScriptMerger()

    def changeTheme(self, theme):
        data.config.theme = theme
        if theme == 'Dark':
            data.app.setPalette(get_dark_palette())
        elif theme == 'Light':
            data.app.setPalette(get_light_palette())
        else:
            data.app.setPalette(get_system_palette())
        data.config.write_config()
        
    def checkTheme(self):
        theme = data.config.theme
        for action in self.menuSelect_Theme.actions():
            if action.text() == theme:
                action.setChecked(True)
                break
