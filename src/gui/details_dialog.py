
'''Details Dialog'''
# pylint: disable=invalid-name

from PySide6 import QtCore
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import QWidget, QHBoxLayout, QTextEdit

from src.globals.constants import translate
from src.domain.mod import Mod


class DetailsDialog(QWidget):
    '''Dialog showing mod details'''

    def __init__(self, parent: QWidget, mod: Mod):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName("Details")
        self.resize(700, 800)
        self.setMinimumSize(600, 600)
        self.layout = QHBoxLayout(self)
        self.layout.setObjectName("layout")
        self.document = QTextDocument()
        self.document.setPlainText(str(mod))
        self.text = QTextEdit(self)
        self.text.setObjectName("text")
        self.text.setDocument(self.document)
        self.text.setAutoFormatting(QTextEdit.AutoAll)
        self.text.setReadOnly(True)
        self.text.setLineWrapMode(QTextEdit.NoWrap)
        self.layout.addWidget(self.text)

        self.setWindowTitle(mod.name + " " + translate("Details", "Details"))
        QtCore.QMetaObject.connectSlotsByName(self)

    def adjustWidth(self):
        '''Fits size to content'''
        self.resize(
            self.document.idealWidth() +
            self.text.contentsMargins().left() + self.text.contentsMargins().right() +
            self.contentsMargins().left() + self.contentsMargins().right() + 50,
            self.height())

    def showEvent(self, event):
        '''Qt show event'''
        super().showEvent(event)
        self.adjustWidth()

    def keyPressEvent(self, event):
        '''Qt KeyPressEvent override'''
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
