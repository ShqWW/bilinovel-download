# coding:utf-8
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QFont

font_label = QFont('幼圆', 18)
font_label.setBold(True)
font_msg = QFont('幼圆', 12)
font_msg.setBold(True)

class EmittingStr(QObject):
    textWritten = pyqtSignal(str)  # 定义一个发送str的信号
    def write(self, text):
        self.textWritten.emit(str(text))
    def flush(self):
        pass
    def isatty(self):
        pass
# sys.stdout = EmittingStr(textWritten=outputWritten)
# sys.stderr = EmittingStr(textWritten=outputWritten)