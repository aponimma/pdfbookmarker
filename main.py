import sys
from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QSize, QThread, QObject, Signal, Slot, QDir
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog
from pdfbookmarker import PdfBookmarker
from contents import Contents

class MainWindow(QWidget):
    """
    MainWindow of pdfbookmarker.
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        # connect worker thread's signal and slot
        self.contents_thread = PdfBookmarkerThread()
        self.contents_thread.contentsGenerated.connect(self.allContentsGenerationDone)
        # construct GUI
        self.text_area = QTextEdit()
        self.push_btn = QPushButton("Get Contents")
        self.push_btn.clicked.connect(self.addContentsGenerationTask)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.push_btn)
        self.layout.addWidget(self.text_area)
        self.setWindowTitle("pdfbookmarker")
        self.setLayout(self.layout)
        self.show()

    @Slot(Contents)
    def allContentsGenerationDone(self, pdfContents):
        self.push_btn.setText("Get Contents")
        self.push_btn.setEnabled(True)
        for entry in pdfContents:
            self.text_area.append("{}, {}, {}".format(entry.title, entry.page, entry.level))

    def addContentsGenerationTask(self):
        """
        Append contents to QTextEdit
        """
        pdfFileName = QFileDialog.getOpenFileName(self, self.tr("Open File"),
                                       QDir.homePath(),
                                       self.tr("PDF file (*.pdf)"))
        if not pdfFileName[0]:
            return
        self.contents_thread.setPdf(pdfFileName[0])
        self.contents_thread.start()
        self.push_btn.setText("Getting...")
        self.push_btn.setEnabled(False)

    def sizeHint(self):
        return QSize(500, 800)

    #def closeEvent(self): # 安全地终止所有进程

class PdfBookmarkerThread(QThread):
    """
    Thread of time-consuming PdfBookmarker.
    """

    contentsGenerationStarted = Signal()
    contentsGenerated = Signal(Contents)

    def __init__(self):
        super(PdfBookmarkerThread, self).__init__()
        self.pdfFileName = "Linear-Algebra-Done-Right.pdf"

    def setPdf(self, pdfFileName):
        self.pdfFileName = pdfFileName

    def run(self):
        #TODO: 是否能够优化执行过程，以便能够随时安全地停止线程
        self.contentsGenerationStarted.emit()
        self.get_contents()
        if self.contents:
            self.contentsGenerated.emit(self.contents)

    def get_contents(self):
        bookmarker = PdfBookmarker(self.pdfFileName)
        self.contents = bookmarker.contents

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
