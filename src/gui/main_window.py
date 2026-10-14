'''Main Window'''

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow

from src.core.fetcher import *


class CustomMainWindow(QMainWindow):
    '''Main Window for drag-and-drop integration'''

    def __init__(self, parent=None, dropCallback=None):
        super().__init__(parent)
        self.dropCallback = dropCallback

    def dragEnterEvent(self, event):
        '''Qt dragEnterEvent override'''
        urls = event.mimeData().urls()
        if not urls:
            event.ignore()
            return
        for url in urls:
            filepath = url.toLocalFile()
            if not isArchive(filepath) and not isValidModFolder(filepath):
                event.ignore()
                return
        event.accept()

    def dropEvent(self, event):
        '''Qt dropEvent override'''
        if self.dropCallback:
            filelist = list(map(lambda url: url.toLocalFile(), event.mimeData().urls()))
            callback = self.dropCallback
            event.acceptProposedAction()
            # Modal prompts must wait until the native drag-and-drop operation has finished.
            QTimer.singleShot(0, self, lambda: callback(filelist))
