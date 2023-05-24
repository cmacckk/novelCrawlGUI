from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

class NovelTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self.headerLabels = ["小说名", "作者", "书籍号", "来源"]

    def rowCount(self, parent=QModelIndex()):
        """ The length of the outer list """
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        """ The following takes the first sub-list, and returns
            the length (only works if all rows are an equal length) """
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """
            See below for the nested-list data structure.
            .row() indexes into the outer list
            .column() indexes into the sub-list
        """
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()
            return str(self._data[row][column])
        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section < len(self.headerLabels):
                return self.headerLabels[section]

        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Vertical:
            return f"{section + 1}"