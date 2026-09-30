'''Details Dialog'''

from PySide6 import QtCore
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QHBoxLayout, QTextEdit, QWidget

from src.domain.mod import Mod
from src.globals.constants import translate


class DetailsDialog(QWidget):
    '''Dialog showing mod details'''

    def __init__(self, parent: QWidget, mod: Mod):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setObjectName("Details")
        self.resize(700, 800)
        self.setMinimumSize(600, 600)
        self.contentLayout = QHBoxLayout(self)
        self.contentLayout.setObjectName("layout")
        self.document = QTextDocument()
        self.document.setPlainText(str(mod))
        self.text = QTextEdit(self)
        self.text.setObjectName("text")
        self.text.setDocument(self.document)
        self.text.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoAll)
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.contentLayout.addWidget(self.text)

        self.setWindowTitle(mod.name + " " + translate("Details", "Details"))
        QtCore.QMetaObject.connectSlotsByName(self)

    def adjustWidth(self):
        '''Fits size to content'''
        self.resize(
            int(self.document.idealWidth())
            + self.text.contentsMargins().left()
            + self.text.contentsMargins().right()
            + self.contentsMargins().left()
            + self.contentsMargins().right()
            + 50,
            self.height(),
        )

    def showEvent(self, event):
        '''Qt show event'''
        super().showEvent(event)
        self.adjustWidth()

    def keyPressEvent(self, event):
        '''Qt KeyPressEvent override'''
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
