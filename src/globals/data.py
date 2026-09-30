'''Global instances'''

from PySide6.QtCore import QTranslator
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from src.configuration.config import Configuration

config: Configuration | None = None
app: QApplication | None = None
dark_palette: QPalette | None = None
light_palette: QPalette | None = None
debug: bool = True
translator: QTranslator = QTranslator()


def getConfig() -> Configuration:
    if config is None:
        raise RuntimeError("Configuration has not been initialized")
    return config


def getApp() -> QApplication:
    if app is None:
        raise RuntimeError("Application has not been initialized")
    return app
