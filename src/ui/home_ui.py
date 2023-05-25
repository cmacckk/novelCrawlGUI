from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QProgressBar, QHeaderView
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from src.ui.novel_table_model import NovelTableModel
from src.ui.center_table_view import CenterTableView
from src.ui.novel_table_view import NovelTableView
from src.thread.search_thread import SearchThread


class HomeUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("小说下载器 by CC")
        self.resize(QSize(500, 650))
        self.setWindowIcon(QIcon("./images/book.png"))

        self.globalVerticalLayout = QVBoxLayout()
        self.globalVerticalLayout.setSpacing(0)

        self.progressBar = QProgressBar()

        self.setupFirstHorizontalLayout()
        self.setupSecondHorizontalLayout()
        self.setupThirdHorizontalLayout()

        self.globalVerticalLayout.addLayout(self.firstHorizontalLayout, stretch=1)
        self.globalVerticalLayout.addLayout(self.secondHorizontalLayout, stretch=1)
        self.globalVerticalLayout.addLayout(self.thirdHorizontalLayout, stretch=1)

        self.setLayout(self.globalVerticalLayout)

    def setupFirstHorizontalLayout(self):
        self.firstHorizontalLayout = QHBoxLayout()
        self.firstHorizontalLayout.setSpacing(0)
        self.firstHorizontalLayout.setContentsMargins(0, 0, 0, 10)

        self.searchButton = QPushButton("搜索")
        self.searchButton.clicked.connect(self.searchEvent)

        self.searchTextLineEdit = QLineEdit()
        self.searchTextLineEdit.editingFinished.connect(self.searchButton.click)
        self.searchTextLineEdit.setPlaceholderText("搜索的小说名")
        self.searchTextLineEdit.setContentsMargins(0, 0, 10, 0)

        self.firstHorizontalLayout.addWidget(self.searchTextLineEdit)
        self.firstHorizontalLayout.addWidget(self.searchButton)

    def setupSecondHorizontalLayout(self):
        self.secondHorizontalLayout = QHBoxLayout()
        self.secondHorizontalLayout.setSpacing(0)
        self.secondHorizontalLayout.setContentsMargins(0, 0, 0, 10)

        self.novelShowTableView = NovelTableView(self.progressBar)

        data = []

        self.novelModel = NovelTableModel(data)
        self.novelShowTableView.setModel(self.novelModel)

        centerTableView = CenterTableView()
        self.novelShowTableView.setItemDelegate(centerTableView)

        self.novelShowTableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.secondHorizontalLayout.addWidget(self.novelShowTableView)

    def setupThirdHorizontalLayout(self):
        self.thirdHorizontalLayout = QHBoxLayout()
        self.thirdHorizontalLayout.setSpacing(0)

        self.thirdHorizontalLayout.addWidget(self.progressBar)

    def searchEvent(self):
        book = self.searchTextLineEdit.text().strip()
        # print(book)
        self.searchThread = SearchThread(book)
        self.searchThread.booksSignal.connect(self.searchSignalEvent)
        self.searchThread.progressSignal.connect(self.searchProgressSignalEvent)
        self.searchThread.start()

    def searchSignalEvent(self, books):
        self.novelShowTableView.setModel(NovelTableModel(books))

    def searchProgressSignalEvent(self, progress):
        self.progressBar.setValue(progress)