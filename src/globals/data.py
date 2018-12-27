'''Global instances'''
# pylint: disable=invalid-name

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator
from src.configuration.config import Configuration

config: Configuration = None
app: QApplication = None
debug: bool = True
translator: QTranslator = QTranslator()
