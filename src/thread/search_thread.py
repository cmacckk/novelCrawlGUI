from PyQt6.QtCore import QThread, pyqtSignal
from src.biquge.bige7 import Bige7
from src.biquge.bige5200 import BiQuGe5200Net
from src.biquge.ibiquge_org import IBiQuGeOrg


class SearchThread(QThread):
    booksSignal = pyqtSignal(list)
    progressSignal = pyqtSignal(int)

    def __init__(self, book, parent=None):
        super().__init__(parent)
        self.book = book

    def run(self):
        bige7BookInfo = Bige7().search_book(self.book)
        self.progressSignal.emit(33)
        bige5200BookInfo = BiQuGe5200Net().search_book(self.book)
        self.progressSignal.emit(66)
        ibiqugeBookInfo = IBiQuGeOrg().search_book(self.book)
        self.progressSignal.emit(100)
        resultList = []
        [resultList.append([bookInfo['book'], bookInfo['author'], bookInfo['book_id'], bookInfo['source']]) for bookInfo in bige7BookInfo]
        [resultList.append([bookInfo['book'], bookInfo['author'], bookInfo['book_id'], bookInfo['source']]) for bookInfo in bige5200BookInfo]
        [resultList.append([bookInfo['book'], bookInfo['author'], bookInfo['book_id'], bookInfo['source']]) for bookInfo in ibiqugeBookInfo]
        self.booksSignal.emit(resultList)