'''Global instances'''
# pylint: disable=invalid-name

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTranslator
from src.configuration.config import Configuration

config: Configuration = None
app: QApplication = None
debug: bool = True
translator: QTranslator = QTranslator()
