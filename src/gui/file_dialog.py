'''File Dialog'''
# pylint: disable=invalid-name

from PyQt5.QtWidgets import QFileDialog, QTreeView

class FileDialog(QFileDialog):
    '''Custom FileDialog'''
    def __init__(self, *args):
        super().__init__(*args)
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.ExistingFiles)
        self.tree = self.findChild(QTreeView)
        self.resize(800, 800)
        self.selectedFiles = None
        self.horizontalLayout = None
        self.exec_()

    def accept(self):
        '''Accept selected files'''
        inds = self.tree.selectionModel().selectedRows(0)
        self.selectedFiles = []
        for i in inds:
            self.selectedFiles.append(str(self.directory().absolutePath()) + "/" + str(i.data()))
        self.close()
