
'''Details Dialog'''
# pylint: disable=invalid-name

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPlainTextEdit

from src.globals.constants import TRANSLATE


class DetailsDialog(QWidget):
    '''Dialog showing mod details'''
    def __init__(self, parent, text):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName("Details")
        self.resize(700, 800)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plainTextEdit = QPlainTextEdit(self)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setPlainText(text)
        self.plainTextEdit.setReadOnly(True)
        self.horizontalLayout.addWidget(self.plainTextEdit)

        self.setWindowTitle(TRANSLATE("Details", "Details"))
        QtCore.QMetaObject.connectSlotsByName(self)

    def keyPressEvent(self, event):
        '''Qt KeyPressEvent override'''
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
