'''Tree Widget'''

import sys

from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem


class CustomTreeWidgetItem(QTreeWidgetItem):
    '''Tree Widget Item for proper ordering'''

    def __init__(self, parent: QTreeWidget | QTreeWidgetItem | list[str] | None = None):
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if not self.text(column) and not otherItem.text(column):
            return self.checkState(column).value < otherItem.checkState(column).value
        try:
            left = int(self.text(column)) if self.text(column) != "-" else sys.maxsize
            right = int(otherItem.text(column)) if otherItem.text(column) != "-" else sys.maxsize
            return left < right
        except ValueError:
            return self.text(column).lower() < otherItem.text(column).lower()
