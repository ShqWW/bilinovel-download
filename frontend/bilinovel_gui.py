# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QRegExp
from PyQt5.QtGui import QTextCursor, QPixmap, QRegExpValidator
from PyQt5.QtWidgets import QFrame, QGridLayout
from qfluentwidgets import TextEdit, ImageLabel, LineEdit, PushButton, ProgressRing, SubtitleLabel, EditableComboBox

import sys
import base64
from resource.book import book_base64
from frontend.cfg_utils import *
from backend.bilinovel.bilinovel_router import downloader_router
from .gui_utils import font_label, font_msg, EmittingStr



class MainThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        sys.stdout = self.parent.msg_out
        sys.stderr = self.parent.msg_out
        
    def run(self):
        self.parent.clear_signal.emit('')
        try:
            book_no = self.parent.editline_book.text()
            volumn_no = self.parent.editline_volumn.text()
            out_path = read_config_dict('download_path')
            interval = read_config_dict('interval')
            num_thread = read_config_dict('numthread')
            downloader_router(out_path, book_no, volumn_no, interval, num_thread, True, self.parent.hang_signal, self.parent.progressring_signal, self.parent.cover_signal, self.parent.editline_hang)
            self.parent.end_signal.emit('')
        except Exception as e:
            self.parent.end_signal.emit('')
            print('错误，请检查网络情况或确认输入是否正确')
            print('错误信息：')
            print(e)
    def terminate(self) -> None:
        result = super().terminate()
        return result
    


class NovelWidget(QFrame):

    progressring_signal = pyqtSignal(object) 
    end_signal = pyqtSignal(object) 
    hang_signal = pyqtSignal(object)
    clear_signal = pyqtSignal(object)
    cover_signal = pyqtSignal(object)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text)
        self.parent = parent
        self.label_book = SubtitleLabel('书号：', self)
        self.label_volumn = SubtitleLabel('卷号：', self)
        self.editline_book = LineEdit(self) 
        self.editline_volumn = LineEdit(self) 
        validator = QRegExpValidator(QRegExp("\\d+"))  # 正则表达式匹配阿拉伯数字
        self.editline_book.setValidator(validator)
        # self.editline_volumn.setValidator(validator)

        self.editline_book.setMaxLength(4)
        # self.editline_volumn.setMaxLength(2)
        
        # self.editline_book.setText('2059')
        # self.editline_volumn.setText('3')
        self.book_icon = QPixmap()
        self.book_icon.loadFromData(base64.b64decode(book_base64))
        self.cover_w, self.cover_h = 152, 230

        self.label_cover = ImageLabel(self.book_icon, self)
        self.label_cover.setBorderRadius(8, 8, 8, 8)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)

        self.text_screen = TextEdit()
        self.text_screen.setReadOnly(True)
        self.text_screen.setFixedHeight(self.cover_h)

        self.progressRing = ProgressRing(self)
        self.progressRing.setValue(0)
        self.progressRing.setTextVisible(True)
        self.progressRing.setFixedSize(50, 50)
        
        self.btn_run = PushButton('确定', self)
        self.btn_run.setShortcut(Qt.Key_Return)
        self.btn_stop = PushButton('取消', self)
        self.btn_hang = PushButton('确定', self)
        
        self.editline_hang = EditableComboBox(self)
        self.gridLayout = QGridLayout(self)
        self.screen_layout = QGridLayout()
        self.btn_layout = QGridLayout()
        self.hang_layout = QGridLayout()
        
        self.label_book.setFont(font_label)
        self.label_volumn.setFont(font_label)
        self.editline_book.setFont(font_label)
        self.editline_volumn.setFont(font_label)
        self.text_screen.setFont(font_msg)
        self.editline_hang.setFont(font_msg)

        self.gridLayout.addWidget(self.editline_book, 0, 1)
        self.gridLayout.addWidget(self.editline_volumn, 1, 1)
        self.gridLayout.addWidget(self.label_book, 0, 0)
        self.gridLayout.addWidget(self.label_volumn, 1, 0)

        self.gridLayout.addLayout(self.btn_layout, 2, 1, 1, 1)
        self.btn_layout.addWidget(self.btn_run, 2, 1)
        self.btn_layout.addWidget(self.btn_stop, 2, 2)

        self.gridLayout.addLayout(self.screen_layout, 3, 0, 2, 2)

        self.screen_layout.addWidget(self.progressRing, 0, 1, Qt.AlignLeft|Qt.AlignBottom)
        self.screen_layout.addWidget(self.text_screen, 0, 0)
        self.screen_layout.addWidget(self.label_cover, 0, 1)
        
        

        self.gridLayout.addLayout(self.hang_layout, 5, 0, 1, 2)
        self.hang_layout.addWidget(self.editline_hang, 0, 0)
        self.hang_layout.addWidget(self.btn_hang, 0, 1)

        self.screen_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.gridLayout.setContentsMargins(20, 10, 20, 10)

        self.btn_run.clicked.connect(self.process_start)
        self.btn_stop.clicked.connect(self.process_stop)
        self.btn_hang.clicked.connect(self.process_continue)

        self.progressring_signal.connect(self.progressring_msg)
        self.end_signal.connect(self.process_end)
        self.hang_signal.connect(self.process_hang)
        self.clear_signal.connect(self.clear_screen)
        self.cover_signal.connect(self.display_cover)

        self.progressRing.hide()
        self.btn_hang.hide()
        self.editline_hang.hide()
        self.btn_stop.setEnabled(False)
        
        self.msg_out = EmittingStr(textWritten=self.outputWritten)

        self.text_screen.setText(self.parent.welcome_text) 
    
    def process_start(self):
        self.label_cover.setImage(self.book_icon)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)
        self.btn_run.setEnabled(False)
        self.btn_run.setText('正在下载')
        self.btn_stop.setEnabled(True)
        self.main_thread = MainThread(self)
        self.main_thread.start()
        
    def process_end(self, input=None):
        self.btn_run.setEnabled(True)
        self.btn_run.setText('开始下载')
        self.btn_run.setShortcut(Qt.Key_Return)
        self.btn_stop.setEnabled(False)
        self.progressRing.hide()
        self.btn_hang.hide()
        self.editline_hang.clear()
        self.editline_hang.hide()
        if input=='refresh':
            self.label_cover.setImage(self.book_icon)
            self.label_cover.setFixedSize(self.cover_w, self.cover_h)
            self.clear_signal.emit('')
            self.text_screen.setText(self.parent.welcome_text) 
        
    def outputWritten(self, text):
        cursor = self.text_screen.textCursor()
        scrollbar=self.text_screen.verticalScrollBar()
        is_bottom = (scrollbar.value()>=scrollbar.maximum() - 15)
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        if is_bottom:
            self.text_screen.setTextCursor(cursor)
        # self.text_screen.ensureCursorVisible()
    
    def clear_screen(self):
        self.text_screen.clear()
    
    def display_cover(self, signal_msg):
        filepath, img_h, img_w = signal_msg
        self.label_cover.setImage(filepath)
        self.label_cover.setFixedSize(int(img_w*self.cover_h/img_h), self.cover_h)
        
    def progressring_msg(self, input):
        if input == 'start':
            self.label_cover.setImage(self.book_icon)
            self.label_cover.setFixedSize(self.cover_w, self.cover_h)
            self.progressRing.show()
        elif input == 'end':
            self.progressRing.hide()
            self.progressRing.setValue(0)
        else:
            self.progressRing.setValue(input)
    
    def process_hang(self, input=None):
        self.btn_hang.setEnabled(True)
        self.btn_hang.setShortcut(Qt.Key_Return)
        self.btn_hang.show()
        self.editline_hang.show()
    
    def process_continue(self, input=None):
        self.btn_hang.hide()
        self.btn_hang.setEnabled(False)
        self.editline_hang.hide()
        
    
    def process_stop(self):
        self.main_thread.terminate()
        self.end_signal.emit('refresh')