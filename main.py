# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (setTheme, Theme, setThemeColor)
import sys
from frontend.mainwindow import MainWindow

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    setTheme(Theme.DARK)
    setThemeColor('#FF7233')
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
