'''Tree Widget'''
# pylint: disable=invalid-name

import sys
from PySide6.QtWidgets import QTreeWidgetItem


class CustomTreeWidgetItem(QTreeWidgetItem):
    '''Tree Widget Item for proper ordering'''
    # pylint: disable=too-few-public-methods,useless-super-delegation

    def __init__(self, parent=None):
        super().__init__(parent)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if (not self.text(column) and not otherItem.text(column)):
            return self.checkState(column) < otherItem.checkState(column)
        try:
            left = int(self.text(column)) if self.text(
                column) != "-" else sys.maxsize
            right = int(otherItem.text(column)) if otherItem.text(
                column) != "-" else sys.maxsize
            return left < right
        except ValueError:
            return self.text(column).lower() < otherItem.text(column).lower()
