from PySide2.QtCore import Qt, QSize, Slot, QDir, QFileInfo, qDebug, qWarning
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import ( QWidget, QTabWidget, QMainWindow, QVBoxLayout, 
    QTextEdit, QPushButton, QFileDialog )
from contents import Contents
from bookmarkerthread import BookmarkerThread
from contentstreeviewer import ContentsTreeViewer

class MainWindow(QMainWindow):
    """
    The MainWindow of pdfbookmarker.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        # connect worker thread's signal and slot
        self.contents_thread = BookmarkerThread()
        self.contents_thread.contentsGenerated.connect(self.allContentsGenerationDone)
        # construct GUI
        self.text_area = QTextEdit()
        self.contentsTreeViewer = ContentsTreeViewer()
        self.resultsTabViewer = QTabWidget()
        self.push_btn = QPushButton("Get Contents")
        self.push_btn.clicked.connect(self.addContentsGenerationTask)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.push_btn)
        # add to TabWidget
        self.resultsTabViewer.addTab(self.contentsTreeViewer, QIcon(), self.tr("Contents"))
        self.resultsTabViewer.addTab(self.text_area, QIcon(), self.tr("Plain Text Results"))
        self.layout.addWidget(self.resultsTabViewer)
        # set central widget
        self.setWindowTitle("pdfbookmarker")
        wgt = QWidget()
        wgt.setLayout(self.layout)
        self.setCentralWidget(wgt)
        self.show()

    @Slot(Contents)
    def allContentsGenerationDone(self, pdfContents):
        self.push_btn.setText("Get Contents")
        self.push_btn.setEnabled(True)
        for entry in pdfContents:
            self.text_area.append("{}, {}, {}".format(entry.title, entry.page, entry.level))
        self.contentsTreeViewer.setContentsData(pdfContents)
        self.contentsTreeViewer.displayContents()

    def addContentsGenerationTask(self):
        """
        Append contents to QTextEdit
        """
        pdfFileName = QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                       QDir.homePath(),
                                       self.tr("PDF file (*.pdf)"))
        if not pdfFileName[0]:
            qWarning("File name is not valid: {}".format(pdfFileName[0]))
            return
        self.contentsTreeViewer.setBookName(QFileInfo(pdfFileName[0]).baseName())
        self.contents_thread.setPdf(pdfFileName[0])
        self.contents_thread.start()
        self.push_btn.setText("Getting...")
        self.push_btn.setEnabled(False)

    def sizeHint(self):
        return QSize(500, 800)

    #def closeEvent(self): # 安全地终止所有进程