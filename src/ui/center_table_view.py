from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyledItemDelegate

class CenterTableView(QStyledItemDelegate):
    """ Let QTableView data text center """
    def paint(self, painter, option, index):
        option.displayAlignment = Qt.AlignmentFlag.AlignCenter
        super().paint(painter, option, index)