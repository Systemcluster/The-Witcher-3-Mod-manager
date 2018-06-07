import os.path as path
import subprocess
import webbrowser

from PyQt5.Qt import *

import Core
from Helpers import *
from ModClass import Mod

_translate = QtCore.QCoreApplication.translate


class Ui_MainWindow(QWidget):
    '''Main Gui Window'''

    def setupUi(self, MainWindow):
        '''GUI initialization'''
        try:
            MainWindow.setObjectName("MainWindow")
            wini = int(getini('WINDOW', 'width')) if getini('WINDOW', 'width') else 1024
            hini = int(getini('WINDOW', 'height')) if getini('WINDOW', 'height') else 720
            MainWindow.resize(wini, hini)
            MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            MainWindow.setWindowOpacity(1.0)
            MainWindow.setStatusTip("")
            MainWindow.setAutoFillBackground(False)
            MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.centralwidget.setObjectName("centralwidget")
            self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
            self.verticalLayout_2.setObjectName("verticalLayout_2")
            self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
            self.treeWidget.setMinimumSize(QtCore.QSize(750, 500))
            self.treeWidget.setUniformRowHeights(True)
            self.treeWidget.setAnimated(True)
            self.treeWidget.setHeaderHidden(False)
            self.treeWidget.setColumnCount(8)
            self.treeWidget.setObjectName("treeWidget")
            self.treeWidget.header().setCascadingSectionResizes(True)
            self.treeWidget.header().setHighlightSections(False)
            self.treeWidget.header().setSortIndicatorShown(True)
            self.horizontalLayout_tree = QtWidgets.QHBoxLayout()
            self.horizontalLayout_tree.setObjectName("horizontalLayout_tree")
            self.horizontalLayout_tree.addWidget(self.treeWidget)
            self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
            self.horizontalLayout_2.setObjectName("horizontalLayout_2")
            self.loadOrder = QtWidgets.QTreeWidget(self.centralwidget)
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
            self.textEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
            self.textEdit.setReadOnly(True)
            self.textEdit.setObjectName("textEdit")
            self.horizontalLayout_2.addWidget(self.textEdit)
            self.verticalLayout = QtWidgets.QVBoxLayout()
            self.verticalLayout.setObjectName("verticalLayout")
            self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pushButton_4.sizePolicy().hasHeightForWidth())
            self.pushButton_4.setSizePolicy(sizePolicy)
            self.pushButton_4.setMinimumSize(QtCore.QSize(250, 50))
            self.pushButton_4.setMaximumSize(QtCore.QSize(350, 16777215))
            self.pushButton_4.setObjectName("pushButton_4")
            self.verticalLayout.addWidget(self.pushButton_4)
            self.pushButton_5 = QtWidgets.QPushButton(self.centralwidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pushButton_5.sizePolicy().hasHeightForWidth())
            self.pushButton_5.setSizePolicy(sizePolicy)
            self.pushButton_5.setMinimumSize(QtCore.QSize(250, 50))
            self.pushButton_5.setMaximumSize(QtCore.QSize(350, 16777215))
            self.pushButton_5.setObjectName("pushButton_5")
            self.verticalLayout.addWidget(self.pushButton_5)
            self.horizontalLayout_2.addLayout(self.verticalLayout)
            self.horizontalLayout_2.setStretch(0, 3)
            self.horizontalLayout_2.setStretch(1, 1)
            self.verticalLayout_2.addLayout(self.horizontalLayout_2)
            self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
            self.progressBar.setProperty("value", 0)
            self.progressBar.setObjectName("progressBar")
            self.verticalLayout_2.addWidget(self.progressBar)
            self.verticalLayout_2.setStretch(0, 4)
            self.verticalLayout_2.setStretch(1, 1)
            MainWindow.setCentralWidget(self.centralwidget)
            self.menubar = QtWidgets.QMenuBar(MainWindow)
            self.menubar.setGeometry(QtCore.QRect(0, 0, 583, 21))
            self.menubar.setObjectName("menubar")
            self.menuFile = QtWidgets.QMenu(self.menubar)
            self.menuFile.setObjectName("menuFile")
            self.menuEdit = QtWidgets.QMenu(self.menubar)
            self.menuEdit.setObjectName("menuEdit")
            self.menuSettings = QtWidgets.QMenu(self.menubar)
            self.menuSettings.setObjectName("menuSettings")
            self.menuSelect_Language = QtWidgets.QMenu(self.menuSettings)
            self.menuSelect_Language.setObjectName("menuSelect_Language")
            self.menuConfigure_Settings = QtWidgets.QMenu(self.menuSettings)
            self.menuConfigure_Settings.setObjectName("menuConfigure_Settings")
            self.menuHelp = QtWidgets.QMenu(self.menubar)
            self.menuHelp.setObjectName("menuHelp")
            MainWindow.setMenuBar(self.menubar)
            self.toolBar = QtWidgets.QToolBar(MainWindow)
            self.toolBar.setObjectName("toolBar")
            MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
            self.actionInstall_Mods = QtWidgets.QAction(MainWindow)
            self.actionInstall_Mods.setIcon(getIcon('Add.ico'))
            self.actionInstall_Mods.setIconVisibleInMenu(False)
            self.actionInstall_Mods.setObjectName("actionInstall_Mods")
            self.actionInstall_Mods.setIconText(_translate('MainWindow', "Add"))
            self.actionRestore_Columns = QtWidgets.QAction(MainWindow)
            self.actionRestore_Columns.setIconVisibleInMenu(False)
            self.actionRestore_Columns.setObjectName("actionRestore_Columns")
            self.actionUninstall_Mods = QtWidgets.QAction(MainWindow)
            self.actionUninstall_Mods.setIcon(getIcon('rem.ico'))
            self.actionUninstall_Mods.setIconVisibleInMenu(False)
            self.actionUninstall_Mods.setObjectName("actionUninstall_Mods")
            self.actionUninstall_Mods.setIconText(_translate('MainWindow', "Remove"))
            self.actionEnable_Disable_Mods = QtWidgets.QAction(MainWindow)
            self.actionEnable_Disable_Mods.setIcon(getIcon('check.ico'))
            self.actionEnable_Disable_Mods.setIconVisibleInMenu(False)
            self.actionEnable_Disable_Mods.setObjectName("actionEnable_Disable_Mods")
            self.actionEnable_Disable_Mods.setIconText(_translate('MainWindow', "Toggle"))
            self.actionRefresh_Mod_List = QtWidgets.QAction(MainWindow)
            self.actionRefresh_Mod_List.setObjectName("actionRefresh_Mod_List")
            self.actionSelect_All_Mods = QtWidgets.QAction(MainWindow)
            self.actionSelect_All_Mods.setObjectName("actionSelect_All_Mods")
            self.actionSetPriority = QtWidgets.QAction(MainWindow)
            self.actionSetPriority.setObjectName("actionSetPriority")
            self.actionUnsetPriority = QtWidgets.QAction(MainWindow)
            self.actionUnsetPriority.setObjectName("actionUnsetPriority")
            self.actionRun_The_Game = QtWidgets.QAction(MainWindow)
            self.actionRun_The_Game.setObjectName("actionRun_The_Game")
            self.actionRun_Script_Merger = QtWidgets.QAction(MainWindow)
            self.actionRun_Script_Merger.setObjectName("actionRun_Script_Merger")
            self.actionAbout = QtWidgets.QAction(MainWindow)
            self.actionAbout.setObjectName("actionAbout")
            self.actionRename = QtWidgets.QAction(MainWindow)
            self.actionRename.setObjectName("actionRename")
            self.actionDetails = QtWidgets.QAction(MainWindow)
            self.actionDetails.setObjectName("actionDetails")
            self.actionMain_Web_Page = QtWidgets.QAction(MainWindow)
            self.actionGitHub = QtWidgets.QAction(MainWindow)
            self.actionMain_Web_Page.setObjectName("actionMain_Web_Page")
            self.actionGitHub.setObjectName("acitionGitHub")
            self.actionAlert_to_run_Script_Merger = QtWidgets.QAction(MainWindow)
            self.actionAlert_to_run_Script_Merger.setCheckable(True)
            self.actionAlert_to_run_Script_Merger.setObjectName("actionAlert_to_run_Script_Merger")
            self.languageActionGroup = QActionGroup(MainWindow)
            for lang in os.listdir('translations/'):
                temp = self.makeLangAction(lang)
                self.languageActionGroup.addAction(temp)
                self.menuSelect_Language.addAction(temp)
            self.actionChange_Game_Path = QtWidgets.QAction(MainWindow)
            self.actionChange_Game_Path.setObjectName("actionChange_Game_Path")
            self.actionChange_Script_Merger_Path = QtWidgets.QAction(MainWindow)
            self.actionChange_Script_Merger_Path.setObjectName("actionChange_Script_Merger_Path")
            self.actionClearOutput = QtWidgets.QAction(MainWindow)
            self.actionClearOutput.setObjectName("actionClearOutput")
            self.menuFile.addAction(self.actionInstall_Mods)
            self.menuFile.addAction(self.actionUninstall_Mods)
            self.menuFile.addAction(self.actionEnable_Disable_Mods)
            self.menuFile.addSeparator()
            self.menuFile.addAction(self.actionRefresh_Mod_List)
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
            self.toolBar.setIconSize(QtCore.QSize(32, 32))
            self.toolBar.addSeparator()
            self.retranslateUi(MainWindow)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)
        except Exception as err:
            self.output(str(err))

    def retranslateUi(self, MainWindow):
        '''GUI positioning and additional initialziation'''
        MainWindow.setWindowTitle(_translate("MainWindow", "The Witcher 3 Mod Manager"))
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Enabled"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Mod Name"))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Priority"))
        self.treeWidget.headerItem().setText(3, _translate("MainWindow", "Data"))
        self.treeWidget.headerItem().setText(4, _translate("MainWindow", "DLC"))
        self.treeWidget.headerItem().setText(5, _translate("MainWindow", "Menu"))
        self.treeWidget.headerItem().setText(6, _translate("MainWindow", "Var"))
        self.treeWidget.headerItem().setText(7, _translate("MainWindow", "Hidden"))
        self.treeWidget.headerItem().setText(8, _translate("MainWindow", "Key"))
        self.treeWidget.headerItem().setText(9, _translate("MainWindow", "Settings"))
        self.treeWidget.headerItem().setText(10, _translate("MainWindow", "Size"))
        self.treeWidget.headerItem().setText(11, _translate("MainWindow", "Date Installed"))
        self.loadOrder.setSortingEnabled(False)
        self.loadOrder.headerItem().setText(0, _translate("MainWindow", "Load Order"))
        self.loadOrder.headerItem().setText(1, _translate("MainWindow", "Priority"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "Output"))
        self.textEdit.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.pushButton_4.setText(_translate("MainWindow", "Run Script Merger"))
        self.pushButton_5.setText(_translate("MainWindow", "Run the Game"))
        self.menuFile.setTitle(_translate("MainWindow", "Mods"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuSelect_Language.setTitle(_translate("MainWindow", "Select Language"))
        self.menuConfigure_Settings.setTitle(_translate("MainWindow", "Configure Settings"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionInstall_Mods.setText(_translate("MainWindow", "Install Mods"))
        self.actionInstall_Mods.setToolTip(
            _translate("MainWindow", "Install one or more Mods from folders or archives"))
        self.actionInstall_Mods.setShortcut("Ctrl+E")
        self.actionRestore_Columns.setText(_translate("MainWindow", "Restore default column widths"))
        self.actionRestore_Columns.setToolTip(_translate("MainWindow", "Restore default column widths"))
        self.actionUninstall_Mods.setText(_translate("MainWindow", "Uninstall"))
        self.actionUninstall_Mods.setToolTip(_translate("MainWindow", "Uninstall one or more selected Mods"))
        self.actionUninstall_Mods.setShortcut("Del")
        self.actionEnable_Disable_Mods.setText(_translate("MainWindow", "Enable/Disable"))
        self.actionEnable_Disable_Mods.setToolTip(_translate("MainWindow", "Enable or disable selected Mods"))
        self.actionEnable_Disable_Mods.setShortcut("Ctrl+Q")
        self.actionRefresh_Mod_List.setText(_translate("MainWindow", "Refresh Mod List"))
        self.actionRefresh_Mod_List.setShortcut("F5")
        self.actionSelect_All_Mods.setText(_translate("MainWindow", "Select All Mods"))
        self.actionSelect_All_Mods.setShortcut("Ctrl+A")
        self.actionRun_The_Game.setText(_translate("MainWindow", "Run the Game"))
        self.actionRun_The_Game.setShortcut("Ctrl+R")
        self.actionRun_Script_Merger.setText(_translate("MainWindow", "Run Script Merger"))
        self.actionRun_Script_Merger.setShortcut("Ctrl+S")
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionAbout.setShortcut("F1")
        self.actionMain_Web_Page.setText(_translate("MainWindow", "Main Web Page"))
        self.actionGitHub.setText(_translate("MainWindow", "GitHub"))
        self.actionMain_Web_Page.setShortcut("Ctrl+F1")
        self.actionGitHub.setShortcut("Ctrl+F2")
        self.actionAlert_to_run_Script_Merger.setText(_translate("MainWindow", "Alert to run Script Merger"))
        self.actionChange_Game_Path.setText(_translate("MainWindow", "Change Game Path"))
        self.actionChange_Script_Merger_Path.setText(_translate("MainWindow", "Change Script Merger Path"))
        self.actionClearOutput.setText(_translate("MainWindow", "Clear Output"))
        self.actionRename.setText(_translate("MainWindow", "Rename"))
        self.actionRename.setShortcut("F2")
        self.actionDetails.setShortcut("F3")
        self.actionDetails.setText(_translate("MainWindow", "Details"))
        self.actionSetPriority.setText(_translate("MainWindow", "Set Priority"))
        self.actionUnsetPriority.setText(_translate("MainWindow", "Remove Priority"))
        self.menuEdit.addAction(self.actionDetails)
        self.menuEdit.addAction(self.actionRename)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSetPriority)
        self.menuEdit.addAction(self.actionUnsetPriority)

        self.treeWidget.header().resizeSection(0, int(getini('WINDOW', 'section0')) if getini('WINDOW',
                                                                                              'section0') else 60)
        self.treeWidget.header().resizeSection(1, int(getini('WINDOW', 'section1')) if getini('WINDOW',
                                                                                              'section1') else 200)
        self.treeWidget.header().resizeSection(2, int(getini('WINDOW', 'section2')) if getini('WINDOW',
                                                                                              'section2') else 50)
        self.treeWidget.header().resizeSection(3, int(getini('WINDOW', 'section3')) if getini('WINDOW',
                                                                                              'section3') else 39)
        self.treeWidget.header().resizeSection(4, int(getini('WINDOW', 'section4')) if getini('WINDOW',
                                                                                              'section4') else 39)
        self.treeWidget.header().resizeSection(5, int(getini('WINDOW', 'section5')) if getini('WINDOW',
                                                                                              'section5') else 39)
        self.treeWidget.header().resizeSection(6, int(getini('WINDOW', 'section6')) if getini('WINDOW',
                                                                                              'section6') else 39)
        self.treeWidget.header().resizeSection(7, int(getini('WINDOW', 'section7')) if getini('WINDOW',
                                                                                              'section7') else 45)
        self.treeWidget.header().resizeSection(8, int(getini('WINDOW', 'section8')) if getini('WINDOW',
                                                                                              'section8') else 39)
        self.treeWidget.header().resizeSection(9, int(getini('WINDOW', 'section9')) if getini('WINDOW',
                                                                                              'section9') else 50)
        self.treeWidget.header().resizeSection(10, int(getini('WINDOW', 'section10')) if getini('WINDOW',
                                                                                                'section10') else 45)
        self.treeWidget.header().resizeSection(11, int(getini('WINDOW', 'section11')) if getini('WINDOW',
                                                                                                'section11') else 120)
        self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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
        self.treeWidget.itemDoubleClicked.connect(self.doubleClick)
        self.treeWidget.header().setStretchLastSection(False)
        self.loadOrder.itemDoubleClicked.connect(self.loadOrderClicked)
        self.onStart()

    def onStart(self):
        '''Initial configuration'''
        gamepath = getini('PATHS', 'gamepath')
        while (True):
            if (not gamepath):
                gamepath = str(
                    QtWidgets.QFileDialog.getOpenFileName(None, _translate("MainWindow", "Select witcher3.exe"),
                                                          "witcher3.exe", "*.exe")[0])
            if (not gamepath):
                sys.exit()
            if (self.checkGamePath(gamepath)):
                setini('PATHS', 'gamepath', gamepath)
                self.configurePaths()
                self.configureSettings()
                self.configureMods()
                self.configureWindow()
                self.configureToolbar()
                break
            else:
                QMessageBox.critical(self, _translate("MainWindow", "Selected file not correct"),
                                     _translate("MainWindow", "'witcher3.exe' file not selected"), QMessageBox.Ok,
                                     QMessageBox.Ok)
                gamepath = ''

    def Run(self, option):
        '''Run game or script merger'''
        try:
            os.startfile(getini('PATHS', option))
        except Exception as err:
            self.output(str(err))

    def Open(self, file):
        '''Open or run any kind of folder/file or executable'''
        try:
            filename, ext = path.splitext(file)
            if (ext == ".exe" or ext == ".bat"):
                dir, name = path.split(file)
                subprocess.Popen(file, cwd=dir)
            else:
                os.startfile(file)
        except Exception as err:
            self.output(str(err))

    # Settings
    def checkGamePath(self, gamepath=""):
        '''Checks to see if given gamepath is correct'''
        if (not gamepath):
            gamepath = getini('PATHS', 'gamepath')
        return path.exists(gamepath) and path.exists(path.dirname(gamepath) + "/../../content")

    def configurePaths(self):
        '''Generates all needed paths based on game path'''
        gamepath = getini('PATHS', 'gamepath')
        for i in range(3):
            gamepath, temp = path.split(gamepath)
        if (not path.exists(gamepath + "/mods")):
            os.mkdir(gamepath + "/mods")
        setini('PATHS', 'mod', gamepath + "/mods")
        setini('PATHS', 'dlc', gamepath + "/dlc")
        setini('PATHS', 'menu', gamepath + "/bin/config/r4game/user_config_matrix/pc")
        setini('PATHS', 'settings', documents + "/The Witcher 3")
        if (not path.exists(documents + "/The Witcher 3 Mod Manager")):
            os.mkdir(documents + "/The Witcher 3 Mod Manager")
        if (not getini('PATHS', 'scriptmerger')):
            setini('PATHS', 'scriptmerger', '')

    def configureWindow(self):
        setini('WINDOW', 'width', "1024")
        setini('WINDOW', 'height', "720")
        setini('WINDOW', 'section0', '60')
        setini('WINDOW', 'section1', '200')
        setini('WINDOW', 'section2', '50')
        setini('WINDOW', 'section3', '39')
        setini('WINDOW', 'section4', '39')
        setini('WINDOW', 'section5', '39')
        setini('WINDOW', 'section6', '39')
        setini('WINDOW', 'section7', '45')
        setini('WINDOW', 'section8', '39')
        setini('WINDOW', 'section9', '50')
        setini('WINDOW', 'section10', '45')
        setini('WINDOW', 'section11', '120')

    def configureSettings(self):
        '''Generates default settings if they are not present'''
        if (not getini('SETTINGS', 'AllowPopups')):
            setini('SETTINGS', 'AllowPopups', str(1))
        if (getini('SETTINGS', 'AllowPopups') == "1"):
            self.actionAlert_to_run_Script_Merger.setChecked(True)
        if (not getini('SETTINGS', 'language')):
            setini('SETTINGS', 'language', 'English.qm')
        if (not config.has_section('TOOLBAR')):
            config.add_section('TOOLBAR')
        self.CheckLanguage()

    def configureMods(self):
        '''Reads all mods data from xml and creates inner mod structure'''
        self.modList = {}
        if (path.exists('installed.xml')):
            tree = XML.parse('installed.xml')
            root = tree.getroot()
            for xmlmod in root.findall('mod'):
                mod = Mod()
                mod.populateFromXml(xmlmod)
                self.modList[mod.name] = mod
        self.RefreshList()

    def configureToolbar(self):
        '''Creates and configures toolbar'''
        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Run('mod'))
        self.actionTemp.setText('M')
        self.actionTemp.setIconText(_translate('MainWindow', 'Mods'))
        self.actionTemp.setIcon(getIcon("mods.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open Mods folder'))
        self.toolBar.addAction(self.actionTemp)

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Run('dlc'))
        self.actionTemp.setText('D')
        self.actionTemp.setIconText(_translate('MainWindow', 'DLC'))
        self.actionTemp.setIcon(getIcon("dlc.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open DLC folder'))
        self.toolBar.addAction(self.actionTemp)

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Run('menu'))
        self.actionTemp.setText('I')
        self.actionTemp.setIconText(_translate('MainWindow', 'Menus'))
        self.actionTemp.setIcon(getIcon("menu.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open Menus folder'))
        self.toolBar.addAction(self.actionTemp)

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Run('settings'))
        self.actionTemp.setText('S')
        self.actionTemp.setIconText(_translate('MainWindow', 'Settings'))
        self.actionTemp.setIcon(getIcon("settings.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open Settings folder'))
        self.toolBar.addAction(self.actionTemp)

        self.toolBar.addSeparator()

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Open(getini('PATHS', 'menu') + '/input.xml'))
        self.actionTemp.setText('Input Xml')
        self.actionTemp.setIcon(getIcon("xml.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open input.xml file'))
        self.toolBar.addAction(self.actionTemp)

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Open(getini('PATHS', 'settings') + '/input.settings'))
        self.actionTemp.setText('Input Settings')
        self.actionTemp.setIcon(getIcon("input.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open input.settings file'))
        self.toolBar.addAction(self.actionTemp)

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Open(getini('PATHS', 'settings') + '/user.settings'))
        self.actionTemp.setText('User Settings')
        self.actionTemp.setIcon(getIcon("user.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open user.settings file'))
        self.toolBar.addAction(self.actionTemp)

        self.actionTemp = QtWidgets.QAction(MainWindow)
        self.actionTemp.triggered.connect(lambda: self.Open(getini('PATHS', 'settings') + '/mods.settings'))
        self.actionTemp.setText('Mods Settings')
        self.actionTemp.setIcon(getIcon("modset.ico"))
        self.actionTemp.setToolTip(_translate("MainWindow", 'Open mods.settings file'))
        self.toolBar.addAction(self.actionTemp)

        self.toolBar.addSeparator()

        for custom in getininovalue('TOOLBAR'):
            self.addToToolbar(custom)
        self.actionAddToToolbar = QtWidgets.QAction(MainWindow)
        self.actionAddToToolbar.triggered.connect(self.addToToolbar)
        self.actionAddToToolbar.setText(_translate("MainWindow", 'Add New..'))

    def openMenu(self, position):
        '''Right click menu on mod list (Left panel)'''
        menu = QMenu()
        menu.addAction(self.actionDetails)
        menu.addSeparator()
        menu.addAction(self.actionSetPriority)
        menu.addAction(self.actionUnsetPriority)
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
        menu = QMenu(MainWindow)
        menu.addAction(self.actionAddToToolbar)
        remove = QMenu(menu)
        remove.setTitle(_translate("MainWindow", "Remove.."))
        actions = self.toolBar.actions()[14:]
        for action in actions:
            temp = self.makeTempAction(action)
            remove.addAction(temp)
            del action
        menu.addAction(remove.menuAction())
        menu.exec_(self.toolBar.mapToGlobal(position))

    def RemoveFromToolbar(self, action):
        '''Creates menu for removing actions from toolbar'''
        self.toolBar.removeAction(action)
        removeininovalue('TOOLBAR', action.text())

    def addToToolbar(self, selected=""):
        '''Adds custom action to the toolbar selected by user'''
        try:
            if (not selected):
                temp = getFile("", "")
                if (temp):
                    selected = temp[0]

            if (selected):
                fileInfo = QtCore.QFileInfo(selected)
                iconProvider = QtWidgets.QFileIconProvider()
                icon = iconProvider.icon(fileInfo)

                dir, file = path.split(selected)
                actionTemp = QtWidgets.QAction(MainWindow)
                actionTemp.triggered.connect(lambda: self.Open(selected))
                actionTemp.setText(selected)
                actionTemp.setIcon(icon)
                actionTemp.setToolTip(file)
                self.toolBar.addAction(actionTemp)
                setininovalue('TOOLBAR', selected)
        except Exception as err:
            self.output(str(err))

    def Restore_Columns(self):
        setini('WINDOW', 'section0', '60')
        setini('WINDOW', 'section1', '200')
        setini('WINDOW', 'section2', '50')
        setini('WINDOW', 'section3', '39')
        setini('WINDOW', 'section4', '39')
        setini('WINDOW', 'section5', '39')
        setini('WINDOW', 'section6', '39')
        setini('WINDOW', 'section7', '45')
        setini('WINDOW', 'section8', '39')
        setini('WINDOW', 'section9', '50')
        setini('WINDOW', 'section10', '45')
        setini('WINDOW', 'section11', '120')
        self.treeWidget.header().resizeSection(0, int(getini('WINDOW', 'section0')) if getini('WINDOW',
                                                                                              'section0') else 60)
        self.treeWidget.header().resizeSection(1, int(getini('WINDOW', 'section1')) if getini('WINDOW',
                                                                                              'section1') else 200)
        self.treeWidget.header().resizeSection(2, int(getini('WINDOW', 'section2')) if getini('WINDOW',
                                                                                              'section2') else 50)
        self.treeWidget.header().resizeSection(3, int(getini('WINDOW', 'section3')) if getini('WINDOW',
                                                                                              'section3') else 39)
        self.treeWidget.header().resizeSection(4, int(getini('WINDOW', 'section4')) if getini('WINDOW',
                                                                                              'section4') else 39)
        self.treeWidget.header().resizeSection(5, int(getini('WINDOW', 'section5')) if getini('WINDOW',
                                                                                              'section5') else 39)
        self.treeWidget.header().resizeSection(6, int(getini('WINDOW', 'section6')) if getini('WINDOW',
                                                                                              'section6') else 39)
        self.treeWidget.header().resizeSection(7, int(getini('WINDOW', 'section7')) if getini('WINDOW',
                                                                                              'section7') else 45)
        self.treeWidget.header().resizeSection(8, int(getini('WINDOW', 'section8')) if getini('WINDOW',
                                                                                              'section8') else 39)
        self.treeWidget.header().resizeSection(9, int(getini('WINDOW', 'section9')) if getini('WINDOW',
                                                                                              'section9') else 50)
        self.treeWidget.header().resizeSection(10, int(getini('WINDOW', 'section10')) if getini('WINDOW',
                                                                                                'section10') else 45)
        self.treeWidget.header().resizeSection(11, int(getini('WINDOW', 'section11')) if getini('WINDOW',
                                                                                                'section11') else 120)


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
                QMessageBox.critical(self, _translate("MainWindow", "Error"),
                                     _translate("MainWindow", "Select only one mod to rename"))
            else:
                oldname = selected[0]
                newname, ok = QInputDialog.getText(self, _translate("MainWindow", 'Rename'),
                                                   _translate("MainWindow", 'Enter new mod name') + ": ",
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
        if (selected):
            if (len(selected) > 1):
                QMessageBox.critical(self, _translate("MainWindow", "Error"),
                                     _translate("MainWindow", "Select only one mod to display"))
            else:
                mod = self.modList[selected[0]]
                self.Details = QtWidgets.QWidget()
                ui = Ui_Details()
                ui.setupUi(self.Details, str(mod))
                self.Details.show()
                app.exec()

    def modToggled(self, item, column):
        '''Triggered when the mod check state is changed. Enables or disables the mod based on the current check state'''
        if item.checkState(column) == QtCore.Qt.Checked:
            self.modList[item.text(1)].enable()
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            self.modList[item.text(1)].disable()
        self.RefreshLoadOrder()

    def doubleClick(self, item, column):
        '''Triggered when double clicked on the mod'''
        self.EnableDisableMods()

    def loadOrderClicked(self, item, column):
        '''Triggered when double clicked on the mod on the right panel. Sets priority'''
        try:
            selected = item.text(0)
            if (selected[0] == '~'):
                QMessageBox.critical(self, _translate("MainWindow", "Error"),
                                     _translate("MainWindow", "You cannot set priority to disabled mod") + " ")
                return
            selectedvalue = item.text(1)
            if (selectedvalue):
                value = int(selectedvalue)
            else:
                value = 0
            data, ok = QInputDialog.getInt(self, _translate("MainWindow", "Set Priority"),
                                           _translate("MainWindow", "Enter new priority") + ": ")
            if (ok):
                setpriority(str(selected), str(data))
                prioritywrite()
                self.RefreshList()
        except Exception as err:
            self.output(str(err))

    def AlertPopupChanged(self):
        '''Triggered when option to alert popup is changed. Saves the change'''
        if (self.actionAlert_to_run_Script_Merger.isChecked()):
            setini('SETTINGS', 'AllowPopups', "1")
        else:
            setini('SETTINGS', 'AllowPopups', "0")

    def ChangeLanguage(self, language):
        '''Triggered when language is changed. Saves the change and restarts the program'''
        setini('SETTINGS', 'language', str(language))
        button = QMessageBox.question(self, _translate("MainWindow", "Change language"), _translate("MainWindow",
                                                                                                    "You need to restart the program to apply the changes.\nDo you want to restart it now?"),
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if (button == QMessageBox.Yes):
            restart_program()

    def CheckLanguage(self):
        '''Checks which language is selected, and checks it'''

        language = getini('SETTINGS', 'language')
        for lang in self.menuSelect_Language.actions():
            if (language == lang.text() + ".qm"):
                lang.setChecked(True)
                break

    def setPriority(self):
        '''Sets the priority of the selected mods'''
        try:
            selected = self.getSelectedMods()
            if (selected):
                data, ok = QInputDialog.getInt(self, _translate("MainWindow", "Set Priority"),
                                               _translate("MainWindow", "Enter new priority") + ": ")
                if (ok):
                    value = str(data)
                    for modname in selected:
                        mod = self.modList[modname]
                        if mod.enabled:
                            mod.setPriority(value)
                        else:
                            self.output(_translate("MainWindow",
                                                   "You cannot set priority to disabled mod") + " '" + modname + "'")
                    prioritywrite()
                    self.RefreshList()
        except Exception as err:
            self.output(str(err))

    def unsetPriority(self):
        '''Removes priority of the selected mods'''
        selected = self.getSelectedMods()
        if (selected):
            for modname in selected:
                mod = self.modList[modname]
                mod.priority = None
                for data in mod.files:
                    priority.remove_section(data)
            prioritywrite()
            self.RefreshList()

    def ChangeGamePath(self):
        '''Changes game path'''
        gamepath = str(QtWidgets.QFileDialog.getOpenFileName(self, _translate("MainWindow", "Select witcher3.exe"),
                                                             getini('PATHS', 'gamepath'), "*.exe")[0])
        if (self.checkGamePath(gamepath)):
            setini('PATHS', 'gamepath', gamepath)
            self.configurePaths()
            self.RefreshList()
        else:
            QMessageBox.critical(self, _translate("MainWindow", "Selected file not correct"),
                                 _translate("MainWindow", "'witcher3.exe' file not selected"), QMessageBox.Ok,
                                 QMessageBox.Ok)

    def ChangeScriptMergerPath(self):
        '''Changes script merger path'''
        mergerpath = str(
            QtWidgets.QFileDialog.getOpenFileName(self, _translate("MainWindow", "Select script merger"),
                                                  getini('PATHS', 'scriptmerger'), "*.exe")[0])
        if (mergerpath):
            setini('PATHS', 'scriptmerger', mergerpath)

    def InstallMods(self):
        '''Installs selected mods'''
        try:
            self.clear()
            file = getFile(getini('PATHS', 'lastpath'), "*.zip *.rar *.7z")
            if (file != None):
                prgrs = 0
                prgrsmax = len(file)
                for mod in file:
                    prgsbefore = 100 * prgrs / prgrsmax
                    prgsafter = 100 * (prgrs + 1) / prgrsmax
                    Core.installMod(self, mod, prgsbefore, prgsafter)
                    prgrs += 1
                    self.setProgress(100 * prgrs / prgrsmax)
                lastpath, name = path.split(file[0])
                setini('PATHS', 'lastpath', lastpath)
                self.setProgress(0)
                self.RefreshList()
                if (path.exists("extracted")):
                    files.rmtree("extracted")
                self.AlertRunScriptMerger()
            else:
                self.output(_translate("MainWindow", "Installation canceled"))
        except Exception as err:
            self.setProgress(0)
            self.output(str(err))

    def UninstallMods(self):
        '''Uninstalls selected mods'''
        try:
            selected = self.getSelectedMods()
            if (selected):
                clicked = QMessageBox.question(self, _translate("MainWindow", "Confirm"),
                                               _translate("MainWindow", "Are you sure you want to uninstall ")
                                               + str(len(selected)) +
                                               _translate("MainWindow", " selected mods"),
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if clicked == QMessageBox.Yes:
                    prgrs = 0
                    prgrsmax = len(selected)
                    for modname in selected:
                        try:
                            Core.uninstall(self.modList[modname])
                            del self.modList[modname]
                        except Exception as err:
                            self.output(str(err))
                        prgrs += 1
                        self.setProgress(100 * prgrs / prgrsmax)
                    self.RefreshList()
                    self.setProgress(0)
                    self.AlertRunScriptMerger()
        except Exception as err:
            self.setProgress(0)
            self.output(str(err))

    def RunTheGame(self):
        '''Runs the game'''
        try:
            gamepath = getini('PATHS', 'gamepath')
            dir, name = path.split(gamepath)
            subprocess.Popen([gamepath], cwd=dir)
        except Exception as err:
            self.output(str(err))

    def RunScriptMerger(self):
        '''Runs script merger'''
        try:
            scriptmergerpath = getini('PATHS', 'scriptmerger')
            if (scriptmergerpath):
                dir, name = path.split(scriptmergerpath)
                subprocess.Popen([scriptmergerpath], cwd=dir)
            else:
                self.ChangeScriptMergerPath()
                scriptmergerpath = getini('PATHS', 'scriptmerger')
                if (scriptmergerpath):
                    dir, name = path.split(scriptmergerpath)
                    subprocess.Popen([scriptmergerpath], cwd=dir)
        except Exception as err:
            self.output(str(err))

    def About(self):
        '''Opens about window'''
        try:
            QMessageBox.about(self, _translate("MainWindow", "About"),
                              _translate("MainWindow", "The Witcher 3 Mod Manager\n"
                                                       "Version: 0.4 BETA\n"
                                                       "Author: Stefan Kostic (stefan3372)\n"
                                                       "Written in: Python v3.6.3\n"
                                                       "Gui: PyQt5\n"
                                                       "\n"
                                                       "Thank you for using The Witcher 3 Mod Manager!"))
        except Exception as err:
            self.output(str(err))

    def MainWebPage(self):
        '''Opens nexus web page'''
        webbrowser.open('https://rd.nexusmods.com/witcher3/mods/2678')

    def OpenGitHub(self):
        '''Opens github'''
        webbrowser.open('https://github.com/stefan3372/The-WItcher-3-Mod-manager.git')

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
                if (item.checkState(0) == QtCore.Qt.Checked):
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
            self.output(str(err))

    # Helpers
    def RefreshList(self):
        '''Refreshes mod list'''
        try:
            self.treeWidget.clear()
            moddata = []
            for mod in self.modList.values():
                moddata += mod.files
                modsize = 0
                for data in mod.files:
                    modsize += get_size(getini('PATHS', 'mod') + "/" + data)
                    modsize += get_size(getini('PATHS', 'mod') + "/~" + data)
                userstr = _translate("MainWindow", 'No')
                if (mod.usersettings):
                    userstr = _translate("MainWindow", 'Yes')
                self.addToList(mod.enabled, mod.name, mod.getPriority(), len(mod.files), len(mod.dlcs),
                               len(mod.menus), len(mod.xmlkeys), len(mod.hidden), len(mod.inputsettings),
                               userstr, modsize, mod.date)
            self.RefreshLoadOrder()
            saveXML(self.modList)
        except Exception as err:
            self.output(str(err))

    def RefreshLoadOrder(self):
        '''Refreshes right panel list - load order'''
        self.loadOrder.clear()
        dirs = []
        for data in os.listdir(getini('PATHS', 'mod')):
            templist = []
            templist.append(data)
            prt = getpriority(data)
            if (prt):
                temp = int(prt)
            else:
                temp = 16777215
            templist.append(temp)
            dirs.append(templist)
        dirs = sorted(dirs, key=getKey)
        for dir in dirs:
            if (isData(dir[0])):
                if (dir[1] == 16777215):
                    res = ''
                else:
                    res = str(dir[1])
                list = [dir[0], res]
                item = QTreeWidgetItem(list)
                item.setTextAlignment(1, Qt.AlignCenter)
                self.loadOrder.addTopLevelItem(item)

    def setProgress(self, currentProgress):
        '''Sets the progress to currentProgress'''
        self.progressBar.setProperty("value", currentProgress)

    def addToList(self, on, name, priority, data, dlc, menu, keys, hidden, inputkeys, settings, size, date):
        '''Adds mod data to the list'''
        if (data == 0):
            datastr = '-'
        else:
            datastr = str(data)
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
        list = ['', str(name), str(priority), datastr, dlcstr, menustr, keystr, hiddenstr, inkeystr, str(settings),
                sizestr, str(date)]
        item = QtWidgets.QTreeWidgetItem(list)
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
        if (not 'ー' in name):
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

    def addMod(self, name, mod):
        '''Adds mod to the inner mod list structure'''
        self.modList[name] = mod

    def makeTempAction(self, action):
        '''Temp function for bypassing actions with same names problem'''
        temp = QAction(action)
        temp.setText(action.toolTip())
        temp.setIcon(action.icon())
        temp.triggered.connect(lambda: self.RemoveFromToolbar(action))
        return temp

    def makeLangAction(self, ts):
        name, ext = path.splitext(ts)
        action = QAction()
        action.setText(name)
        action.setToolTip(name)
        action.setCheckable(True)
        action.setChecked(False)
        action.triggered.connect(lambda: self.ChangeLanguage(ts))
        return action

    def MessageRebindedKeys(self, key, temp):
        '''Shows dialog to let user decide what to do if rebinded key is found'''
        return QMessageBox.question(self, _translate("MainWindow", "Rebinded key found"),
                                    _translate("MainWindow", "Rebinded key found") + "\n" +
                                    _translate("MainWindow", "Original key") + ": \n" + str(key) + "\n" +
                                    _translate("MainWindow", "Current key") + ": " + str(temp) + "\n\n" +
                                    _translate("MainWindow", "Do you wish to keep your current key?"),
                                    QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.No | QMessageBox.NoToAll | QMessageBox.SaveAll,
                                    QMessageBox.Yes)

    def MessageOverwrite(self, modname):
        '''Shows dialog to let user decide what to do if mod is already installed'''
        return QMessageBox.question(self, _translate("MainWindow", "Mod allready installed"),
                                    "'" + modname + "' " + _translate("MainWindow",
                                                                      "is already installed\nDo you want to remove old one first?"),
                                    QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.No | QMessageBox.NoToAll | QMessageBox.Cancel,
                                    QMessageBox.No)

    def MessageAlertScript(self):
        '''Shows dialog to let user know he/she should run script merger after each change in the mod list'''
        return QMessageBox.question(self, _translate("MainWindow", "Run Script Merger"), _translate("MainWindow",
                                                                                                    "After changing the mod list in any way you should run script merger to merge the mods and ensure their compatibility and remove previously merged scripts\n"
                                                                                                    "Do you want to run it now?\n"
                                                                                                    "\n"
                                                                                                    "Note: You can disable these alerts in the settings..."),
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def AlertRunScriptMerger(self):
        '''Shows previous dialog based on settings'''
        if (getini('SETTINGS', 'allowpopups') == "1"):
            res = self.MessageAlertScript()
            if (res == QMessageBox.Yes):
                self.RunScriptMerger()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    initconfig()
    language = getini('SETTINGS', 'language')
    if (language and path.exists("translations/" + language)):
        translator = QtCore.QTranslator()
        translator.load("translations/" + language)
        app.installTranslator(translator)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    app.setWindowIcon(getIcon("w3a.ico"))
    MainWindow.show()

    ret = app.exec_()
    savewindowsettings(ui, MainWindow)
    iniwrite()
    saveXML(ui.modList)

    sys.exit(ret)
