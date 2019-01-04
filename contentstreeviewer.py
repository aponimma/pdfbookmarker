from PySide2.QtCore import Qt, Slot, Signal, qDebug, qWarning
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from contents import Contents

class ContentsTreeViewer(QTreeWidget):

    def __init__(self):
        QTreeWidget.__init__(self)
        self.setColumnCount(3)
        self.setHeaderLabels([self.tr("Title"), self.tr("Page"), self.tr("Level")])
        self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

    def setBookName(self, strBookName):
        """
        Set PDF book name to tree root.
        """
        if not strBookName:
            return
        self.root = QTreeWidgetItem(self)
        self.root.setText(0, strBookName)
        self.root.setText(1, str(0))
        self.root.setText(2, str(0))

    def setContentsData(self, pdfContents):
        self.contents = pdfContents

    def displayContents(self):
        """
        Build a tree-shapped contents.
        """
        if not self.contents:
            return
        lastItem=self.root
        for entry in self.contents:
            newItem = QTreeWidgetItem([entry.title, str(entry.page), str(entry.level)])
            if not newItem:
                qWarning("QTreeWidgetItem not exits!")
            self.buildContentsTree(lastItem, newItem)
            lastItem = newItem

    def buildContentsTree(self, lastItem, newItem):
        if not lastItem:
            return
        if int(newItem.text(2)) == int(lastItem.text(2)):
            if not lastItem.parent():
                qWarning("Cannot locate item: {}".format(newItem.text(0)))
            lastItem.parent().addChild(newItem)
        elif int(newItem.text(2)) > int(lastItem.text(2)):
            lastItem.addChild(newItem)
        elif int(newItem.text(2)) < int(lastItem.text(2)):
            self.buildContentsTree(lastItem.parent(), newItem)

class ContentsTreeItem(QTreeWidgetItem):

    def __init__(self):
        QTreeWidgetItem.__init__(self)