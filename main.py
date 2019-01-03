"""
Main
"""
import sys
from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QSize, QThread
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from pdfbookmarker import PdfBookmarker

class MainWindow(QWidget):
    """
    MainWindow of pdfbookmarker.
    """

    def __init__(self):
        QWidget.__init__(self)
        self.contents_thread = PdfBookmarkerThread()
        self.text_area = QTextEdit()
        self.push_btn = QPushButton("Get Contents")
        self.push_btn.clicked.connect(self.onGetContentsClicked)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.push_btn)
        self.layout.addWidget(self.text_area)
        self.setWindowTitle("pdfbookmarker")
        self.setLayout(self.layout)
        self.show()

    def onGetContentsClicked(self):
        """
        Append contents to QTextEdit
        """
        self.push_btn.setText("Getting...")
        self.push_btn.setEnabled(False)
        self.contents_thread.start()

    def get_contents(self):
        bookmarker = PdfBookmarker("Linear-Algebra-Done-Right.pdf")
        for entry in bookmarker.contents:
            self.text_area.append("{}, {}, {}".format(entry.title, entry.page, entry.level))

    def sizeHint(self):
        return QSize(500, 800)

    #def closeEvent(self): # 安全地终止所有进程

class PdfBookmarkerThread(QThread):
    """
    Thread of time-consuming PdfBookmarker.
    """
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        #TODO: 是否能够优化执行过程，以便能够随时安全地停止线程
        self.get_contents()

    def get_contents(self):
        bookmarker = PdfBookmarker("Linear-Algebra-Done-Right.pdf")
        self.contents = bookmarker.contents

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
