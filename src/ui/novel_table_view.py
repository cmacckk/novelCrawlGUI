from PyQt6.QtWidgets import QTableView, QMenu, QApplication, QProgressBar, QFileDialog, QMessageBox
from PyQt6.QtCore import QVariant, Qt, QThreadPool, QRunnable, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QAction, QKeySequence
from collections import OrderedDict
from os.path import join
from src.biquge.bige7 import Bige7
from src.biquge.bige5200 import BiQuGe5200Net
from src.biquge.ibiquge_org import IBiQuGeOrg


class NovelTableView(QTableView):
    def __init__(self, progressBar: QProgressBar, parent=None):
        super().__init__(parent)
        self.progressBar = progressBar
        self.threadPool = QThreadPool()
        self.resultList = []
        self.threadIDList = []
        self.novelName = ''
        self.outputPath = './'

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

        downloadAction = QAction("下载", self)
        contextMenu.addAction(downloadAction)

        # connect $contextMenu signal slot
        copyAction.triggered.connect(self.copySelected)
        downloadAction.triggered.connect(self.downloadSelectedNovel)

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

    def downloadSelectedNovel(self):
        """ download select row novel
            Note: when select multi row, only download first row novel
        """
        try:
            selection_model = self.selectionModel()
            # get select row index list
            selected_indexes = selection_model.selectedIndexes()
            if selected_indexes:
                index = selected_indexes[0]
                row_index = index.row()
                # get model data
                model = self.model()
                # get row data
                rowData = []
                for column in range(model.columnCount()):
                    item = model.index(row_index, column).data()
                    rowData.append(item)
                # print(row_data)
                novelName = f"{rowData[0]}-{rowData[1]}-{rowData[3]}"

                self.outputPath = QFileDialog.getExistingDirectory(self, "Select Output Path", "./", QFileDialog.Option.ShowDirsOnly)
                # print(self.outputPath)
                # setting process bar to 0
                self.progressBar.setValue(0)
                self.resultList = []
                self.threadIDList = []
                self.results = {}
                # get novel name and chapter urls
                if rowData[3] == 'bqg70':
                    _, chapterUrlList = Bige7().getBiGe7CrawlUrls("https://www.bqg70.com/book/" + rowData[2])
                if rowData[3] == 'biqu5200':
                    _, chapterUrlList = BiQuGe5200Net().crawl_book_chapter_urls(rowData[2])
                if rowData[3] == 'ibiquge':
                    _, chapterUrlList = IBiQuGeOrg().crawl_book_chapter_urls(rowData[2])

                self.novelName = novelName

                self.totalUrls = len(chapterUrlList)
                self.completedUrls = 0
                self.startDownload(rowData[3], chapterUrlList)
        except ValueError as e:
            print(e)
            return
    def updateProgress(self, value):
        self.progressBar.setValue(value)

    def startDownload(self, siteType: str, chapterUrlList: list):
        self.completedUrls = 0
        for threadID, url in enumerate(chapterUrlList):
            self.startSingleDownloadThread(url, siteType, threadID)

    def startSingleDownloadThread(self, url, siteType: str, threadID: int):
        # create download thread
        download_thread = CrawlNovelThread(url, siteType, threadID)
        # connect thread signal slot
        download_thread.signals.finishedSignal.connect(self.completeCrawling)
        download_thread.signals.resultSignal.connect(self.updateNovelContent)
        # start thread
        self.threadPool.start(download_thread)

    def completeCrawling(self):
        self.completedUrls += 1
        progress = int((self.completedUrls / self.totalUrls) * 100)
        self.updateProgress(progress)

        if self.completedUrls == self.totalUrls:
            for i, value in enumerate(self.resultList):
                self.results[self.threadIDList[i]] = value

            # sort results by threadID
            # chapter title is in order
            sortedResults = OrderedDict(sorted(self.results.items(), key=lambda x: x[0]))

            QMessageBox.about(self, "Done", "小说下载完成，文件已保存到" + join(self.outputPath,self.novelName) + '.txt')

            with open(join(self.outputPath,self.novelName) + '.txt', "w", encoding='utf-8') as file:
                for key, chapter in sortedResults.items():
                    print(key)
                    file.write(chapter['title'] + '\n\n' +
                            chapter['content'] + '\n')


    def updateNovelContent(self, threadID: int, resultDict: dict):
        self.threadIDList.append(threadID)
        self.resultList.append(resultDict)


class CrawlNovelThreadSignals(QObject):
    finishedSignal = pyqtSignal()
    resultSignal = pyqtSignal(int, dict)


class CrawlNovelThread(QRunnable):
    def __init__(self, url, siteType: str, threadID: int):
        super().__init__()
        self.url = url
        self.siteType = siteType
        self.threadID = threadID
        self.signals = CrawlNovelThreadSignals()

    @pyqtSlot()
    def run(self):
        try:
            if self.siteType == 'bqg70':
                resultDict = Bige7().getBiGe7SpotSingleChapterTitleContent(self.url)
            if self.siteType == 'biqu5200':
                resultDict = BiQuGe5200Net().crawl_chapter_title_content(self.url)
            if self.siteType == 'ibiquge':
                resultDict = IBiQuGeOrg().crawl_chapter_title_content(self.url)
            self.signals.resultSignal.emit(self.threadID, resultDict)
        except:
            self.signals.resultSignal.emit(self.threadID, {"title": "Error", "Content": "Error"})
        finally:
            self.signals.finishedSignal.emit()