from PyQt6.QtCore import QThread, pyqtSignal

from src.biquge.biquge70 import Biquge70
from src.biquge.biquge5200 import Biquge5200
from src.log.log import LOGGER

class SearchThread(QThread):
    books_signal = pyqtSignal(list)
    progress_signal = pyqtSignal(int)

    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.book = book

    def run(self):
        result_list = []
        book_info_70 = Biquge70().search_book(self.book)
        _ = [result_list.append([book_info['book'], book_info['author'], book_info['book_id'], book_info['source']]) for book_info in book_info_70]
        self.progress_signal.emit(50)
        book_info_5200 = Biquge5200().search_book(self.book)
        _ = [result_list.append([book_info['book'], book_info['author'], book_info['book_id'], book_info['source']]) for book_info in book_info_5200]
        self.progress_signal.emit(100)
        self.books_signal.emit(result_list)