from PySide2.QtCore import QThread, Signal
from pdfbookmarker import PdfBookmarker
from contents import Contents

class BookmarkerThread(QThread):
    """
    Thread of time-consuming PdfBookmarker.
    """

    contentsGenerationStarted = Signal()
    contentsGenerated = Signal(Contents)

    def __init__(self):
        QThread.__init__(self)
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
