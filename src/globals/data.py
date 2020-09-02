'''Global instances'''
# pylint: disable=invalid-name

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTranslator
from src.configuration.config import Configuration

config: Configuration = None
app: QApplication = None
debug: bool = True
translator: QTranslator = QTranslator()
