import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication
from mainwindow import MainWindow

if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())
