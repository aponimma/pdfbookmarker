from PySide2.QtCore import Qt, QSize, Slot, QDir, QFileInfo, qDebug, qWarning
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import ( QWidget, QTabWidget, QMainWindow, QVBoxLayout, 
    QTextEdit, QPushButton, QFileDialog, QAction, QLabel )
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
        self.pdfFileName = ""
        self.contents_thread = BookmarkerThread()
        self.contents_thread.contentsGenerated.connect(self.allContentsGenerationDone)
        # actoions and menus
        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        # construct GUI
        self.text_area = QTextEdit()
        self.contentsTreeViewer = ContentsTreeViewer()
        self.resultsTabViewer = QTabWidget()
        self.layout = QVBoxLayout()
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

    def createActions(self):
        # Open File Action
        self.openFileAction = QAction(self.tr("Open"))
        self.openFileAction.setStatusTip(self.tr("Set target file to parse contents."))
        self.openFileAction.triggered.connect(self.openFile)
        self.exitAction = QAction(self.tr("E&xit"))
        self.exitAction.setShortcut(self.tr("Ctrl+Q"))
        self.exitAction.setStatusTip(self.tr("Exit the application."))
        self.exitAction.triggered.connect(self.close)
        # Generation Contents Action
        self.startGenerationAction = QAction(self.tr("Start"))
        self.startGenerationAction.setStatusTip(self.tr("Start contents generation of PDF file."))
        self.startGenerationAction.triggered.connect(self.addContentsGenerationTask)
        return

    def createMenus(self):
        # File Menu
        self.fileMenu = self.menuBar().addMenu(self.tr("&File"))
        self.fileMenu.addAction(self.openFileAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        # Command Menu
        self.commandMenu = self.menuBar().addMenu(self.tr("Command"))
        self.commandMenu.addAction(self.openFileAction)
        return

    def createToolBars(self):
        self.fileToolBar = self.addToolBar(self.tr("&File"))
        self.fileToolBar.addAction(self.openFileAction)
        self.commandToolBar = self.addToolBar(self.tr("Command"))
        self.commandToolBar.addAction(self.startGenerationAction)
        return
    
    def createContextMenu(self):
        return

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))
        return

    def setPdfFile(self, strPdfFileName):
        if not strPdfFileName:
            return
        self.pdfFileName = strPdfFileName
        self.setWindowTitle("pdfbookmarker - {}".format(strPdfFileName))

    def showOpenFileDialog(self):
        pdfFileName = QFileDialog.getOpenFileName(self, 
                                    self.tr("&Open File"),
                                    QDir.homePath(),
                                    self.tr("PDF file (*.pdf)"))
        if not pdfFileName[0]:
            return ""
        else:
            return pdfFileName[0]

    def openFile(self):
        self.setPdfFile(self.showOpenFileDialog())

    @Slot(Contents)
    def allContentsGenerationDone(self, pdfContents):
        self.startGenerationAction.setText("Start")
        self.startGenerationAction.setEnabled(True)
        for entry in pdfContents:
            self.text_area.append("{}, {}, {}".format(entry.title, 
                entry.page, entry.level))
        self.contentsTreeViewer.setContentsData(pdfContents)
        self.contentsTreeViewer.displayContents()

    def addContentsGenerationTask(self):
        """
        Append contents to QTextEdit
        """
        if not self.pdfFileName:
            pdfFileName = self.showOpenFileDialog()
            if not pdfFileName:
                qWarning("""File name is not valid: {}\n
                            Generation will be cancelled...""".format(pdfFileName))
                return
            else:
                self.setPdfFile(pdfFileName)
        self.contentsTreeViewer.setBookName(QFileInfo(self.pdfFileName).baseName())
        self.contents_thread.setPdf(self.pdfFileName)
        self.contents_thread.start()
        self.startGenerationAction.setText("Getting...")
        self.startGenerationAction.setEnabled(False)
        self.statusBar().showMessage("Generating contents of {}".format(self.pdfFileName))

    def sizeHint(self):
        return QSize(500, 800)

    #def closeEvent(self): # 安全地终止所有进程