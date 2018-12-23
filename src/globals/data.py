'''Global instances'''
# pylint: disable=invalid-name

from PyQt5.QtWidgets import QApplication
from src.configuration.config import Configuration

config: Configuration = None
app: QApplication = None
debug: bool = True
