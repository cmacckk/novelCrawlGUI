from PyQt6.QtWidgets import QTableView, QMenu, QApplication
from PyQt6.QtCore import QVariant, Qt
from PyQt6.QtGui import QAction, QKeySequence

class NovelTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        """ accomplish copy action """
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copySelected()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        copyAction = QAction("复制", self)
        copyShortcut = QKeySequence(QKeySequence.StandardKey.Copy)
        copyAction.setShortcut(copyShortcut)
        contextMenu.addAction(copyAction)

        # connect $contextMenu signal slot
        copyAction.triggered.connect(self.copySelected)

        contextMenu.exec(event.globalPos())

    def copySelected(self):
        """ accomplish copy action """
        selection = self.selectionModel().selection()
        if not selection.isEmpty():
            text = ""
            rows = sorted(set(index.row() for index in selection.indexes()))
            cols = sorted(set(index.column() for index in selection.indexes()))
            for row in rows:
                rowText = ""
                for col in cols:
                    index = self.model().index(row, col)
                    data = index.data()
                    if data is not None:
                        rowText += str(data)
                    rowText += "\t"
                text += rowText[:-1] + "\n"
            clipboard = QApplication.clipboard()
            clipboard.setText(text)