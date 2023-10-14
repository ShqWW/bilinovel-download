# coding:utf-8
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QFileDialog
from qfluentwidgets import (setTheme, Theme, PushSettingCard, SettingCardGroup, ExpandLayout, TextEdit, ImageLabel, LineEdit, PushButton, Theme,
                            ProgressRing, setTheme, Theme, setFont, OptionsSettingCard, OptionsConfigItem, OptionsValidator, FluentWindow, SubtitleLabel, NavigationItemPosition, setThemeColor)
from qfluentwidgets import FluentIcon as FIF
import threading
import base64
from resource.logo import logo_base64
from resource.book import book_base64
from bilinovel import *
from enum import Enum
from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig



font = QFont()
font.setFamily("YouYuan")
font.setWeight(50)
font.setPointSize(18)
font.setStyleName("Bold")

fontmsg = QFont()
fontmsg.setFamily("YouYuan")
fontmsg.setPointSize(12)
fontmsg.setStyleName("Bold")

class EmittingStr(QObject):
    textWritten = pyqtSignal(str)  # 定义一个发送str的信号
    def write(self, text):
        self.textWritten.emit(str(text))
    def flush(self):
        pass
    def isatty(self):
        pass

class SettingWidget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)

        self.parent = parent
        self.expandLayout = ExpandLayout(self)
        self.setObjectName(text.replace(' ', '-'))
        self.setting_group = SettingCardGroup(self.tr("下载设置"), self)
        
        self.download_path_card = PushSettingCard(
            self.tr('选择文件夹'),
            FIF.DOWNLOAD,
            self.tr("下载目录"),
            self.parent.out_path,
            self.setting_group
        )
        self.themeMode = OptionsConfigItem(
        None, "ThemeMode", Theme.DARK, OptionsValidator(Theme), None)

        self.theme_card = OptionsSettingCard(
            self.themeMode,
            FIF.BRUSH,
            self.tr('应用主题'),
            self.tr("更改外观"),
            texts=[
                self.tr('亮'), self.tr('暗'),
                self.tr('跟随系统设置')
            ],
            parent=self.parent
        )

        self.setting_group.addSettingCard(self.download_path_card)
        self.setting_group.addSettingCard(self.theme_card)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 10, 20, 0)
        self.expandLayout.addWidget(self.setting_group)

        self.download_path_card.clicked.connect(self.download_path_changed)
        self.theme_card.optionChanged.connect(self.theme_changed)

    def download_path_changed(self):
        """ download folder card clicked slot """
        self.parent.out_path = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), self.parent.out_path)
        self.download_path_card.contentLabel.setText(self.parent.out_path)
    
    def theme_changed(self):
        theme_name = self.theme_card.choiceLabel.text()
        self.parent.set_theme(theme_name)


            

class HomeWidget(QFrame):

    progressring_signal = pyqtSignal(object) 
    end_signal = pyqtSignal(object) 
    hang_signal = pyqtSignal(object)
    clear_signal = pyqtSignal(object)
    cover_signal = pyqtSignal(object)

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # self.label = (text, self)
        self.setObjectName(text)
        self.parent = parent
        self.label_book = SubtitleLabel('书号：', self)
        # self.label_book = SubtitleLabel('shuhao1')
        self.label_volumn = SubtitleLabel('卷号：', self)
        # self.editline_book.setText('2059')
        # self.editline_volumn.setText('3')
        
        self.book_icon = QPixmap()
        self.book_icon.loadFromData(base64.b64decode(book_base64))
        self.cover_w, self.cover_h = 110, 160

        self.label_cover = ImageLabel(self.book_icon, self)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)


        self.text_screen = TextEdit()
        self.text_screen.setFixedHeight(self.cover_h)

        self.progressRing = ProgressRing(self)
        self.progressRing.setValue(0)
        self.progressRing.setTextVisible(True)
        self.progressRing.setFixedSize(60, 60)
        
        self.btn_run = PushButton('开始下载', self)
        self.btn_stop = PushButton('取消', self)
        self.hang_btn = PushButton('确定', self)
        
        self.editline_hang = LineEdit(self)
        self.editline_book = LineEdit(self) 
        self.editline_volumn = LineEdit(self) 
        self.gridLayout = QGridLayout(self)
        self.screen_layout = QGridLayout()
        self.btn_layout = QGridLayout()
        self.hang_layout = QGridLayout()
        

        self.label_book.setFont(font)
        self.label_volumn.setFont(font)
        self.editline_book.setFont(font)
        self.editline_volumn.setFont(font)
        self.text_screen.setFont(fontmsg)
        self.editline_hang.setFont(fontmsg)

        

        
        self.gridLayout.addWidget(self.editline_book, 0, 1)
        self.gridLayout.addWidget(self.editline_volumn, 1, 1)
        self.gridLayout.addWidget(self.label_book, 0, 0)
        self.gridLayout.addWidget(self.label_volumn, 1, 0)

        self.gridLayout.addLayout(self.btn_layout, 2, 1, 1, 1)
        self.btn_layout.addWidget(self.btn_run, 2, 1)
        self.btn_layout.addWidget(self.btn_stop, 2, 2)
        
        

        self.gridLayout.addLayout(self.screen_layout, 3, 0, 2, 2)

        self.screen_layout.addWidget(self.text_screen, 0, 0)
        self.screen_layout.addWidget(self.label_cover, 0, 1)
        self.screen_layout.addWidget(self.progressRing, 0, 2)

        self.gridLayout.addLayout(self.hang_layout, 5, 0, 1, 2)
        self.hang_layout.addWidget(self.editline_hang, 0, 0)
        self.hang_layout.addWidget(self.hang_btn, 0, 1)

        self.screen_layout.setContentsMargins(0,0,0,0)
        self.btn_layout.setContentsMargins(0,0,0,0)
        self.gridLayout.setContentsMargins(20, 10, 20, 10)

        self.btn_run.clicked.connect(self.process_start)
        self.btn_stop.clicked.connect(self.set_stop_flag)
        self.hang_btn.clicked.connect(self.process_continue)

        self.progressring_signal.connect(self.progress_msg)
        self.end_signal.connect(self.end_progress)
        self.hang_signal.connect(self.process_hang)
        self.clear_signal.connect(self.clear_screen)
        self.cover_signal.connect(self.display_cover)

        self.progressRing.hide()
        self.hang_btn.hide()
        self.editline_hang.hide()
        self.btn_stop.setEnabled(False)
        
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
        self.text_screen.setText(self.parent.welcome_text) 

    def process_start(self):
        self.label_cover.setImage(self.book_icon)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)
        self.btn_run.setEnabled(False)
        self.btn_run.setText('正在下载')
        self.btn_stop.setEnabled(True)
        self.clear_signal.emit('')
        self.thread = threading.Thread(target=self.main_threading, args=[])
        self.thread.daemon=True
        self.thread.start()
        

    def end_progress(self, input=None):
        self.btn_run.setEnabled(True)
        self.btn_run.setText('开始下载')
        self.btn_stop.setEnabled(False)
        self.progressRing.hide()
        self.hang_btn.hide()
        self.editline_hang.clear()
        self.editline_hang.hide()
        if input=='refresh':
            self.label_cover.setImage(self.book_icon)
            self.label_cover.setFixedSize(self.cover_w, self.cover_h)
            self.clear_signal.emit('')
            self.text_screen.setText(self.parent.welcome_text) 
        
    
    def outputWritten(self, text):
        cursor = self.text_screen.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.text_screen.setTextCursor(cursor)
        self.text_screen.ensureCursorVisible()
    
    def clear_screen(self):
        self.text_screen.clear()
    
    def display_cover(self, filepath):
        self.label_cover.setImage(filepath)
        self.label_cover.setFixedSize(self.cover_w, self.cover_h)

    def main_threading(self):
        try:
            book_no = self.editline_book.text()
            volumn_no = int(self.editline_volumn.text())
            self.editer = Editer(root_path=self.parent.out_path, book_no=book_no, volume_no=volumn_no)
            print('正在获取书籍信息....')
            volume = self.editer.get_index_url()
            print(self.editer.title + '-' + volume['name'], self.editer.author)
            print('****************************')
            if not self.editer.is_buffer():
                print('正在下载文本....')
                if self.editer.stop_flag:
                    return
                volume = self.editer.check_volume(volume, is_gui=True, signal=self.hang_signal, editline=self.editline_hang)

                if self.editer.stop_flag:
                    return
                self.editer.get_text(volume)

                if self.editer.stop_flag:
                    return
                self.editer.buffer(volume)
            else:
                print('检测到文本文件，直接下载插图')
                volume = self.editer.buffer(volume)
            
            if self.editer.stop_flag:
                return

            print('正在下载插图....')
            self.editer.get_image(is_gui=True, signal=self.progressring_signal)

            if self.editer.stop_flag:
                return
            print('正在编辑元数据....')
            self.editer.get_cover(is_gui=True, signal = self.cover_signal)
            self.editer.get_toc(volume)
            self.editer.get_content(volume)
            self.editer.get_epub_head()

            print('正在生成电子书....')
            epub_file = self.editer.get_epub(volume)
            self.clear_signal.emit('')
            print('生成成功！')
            print(f'电子书路径【{epub_file}】')

            self.end_signal.emit('')
        except Exception as e:
            self.clear_signal.emit('')
            self.end_signal.emit('')
            print('错误，请检查网络情况或确认输入是否正确')
        
    def progress_msg(self, input):
        if input == 'start':
            self.progressRing.show()
        elif input == 'end':
            self.progressRing.hide()
        else:
            self.progressRing.setValue(input)
    
    def process_hang(self, input=None):
        self.hang_btn.show()
        self.editline_hang.show()
    
    def process_continue(self, input=None):
        self.editer.hang_flag=False
        self.hang_btn.hide()
        self.editline_hang.hide()
    
    def set_stop_flag(self):
        self.editer.stop_flag = True
        self.end_signal.emit('refresh')
        
        
    

class Window(FluentWindow):

    def __init__(self):
        super().__init__()

        self.out_path = 'C:/Users/haoru/Downloads' 
        self.welcome_text = '搜索小说请登录哔哩轻小说手机版https://www.bilinovel.com，查询后请根据书籍网址输入书号，并根据需要输入下载的卷号。例如小说网址是https://www.bilinovel.com/novel/2704.html并想下载第二卷，则书号输入2704，卷号输入2。'
        self.homeInterface = HomeWidget('Home Interface', self)
        self.settingInterface = SettingWidget('Setting Interface', self)
        self.initNavigation()
        self.initWindow()
        
        
    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主界面')
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(600, 355)
        
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(logo_base64))
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle('哔哩轻小说EPUB下载器')
        self.setFont(font)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
    
    def set_theme(self, mode=None):
        if mode=='亮':
            setTheme(Theme.LIGHT)
        elif mode=='暗':
            setTheme(Theme.DARK)
        elif mode=='跟随系统设置':
            setTheme(Theme.AUTO)
        theme = qconfig.theme
        if theme == Theme.DARK:
            self.homeInterface.label_book.setTextColor(QColor(255,255,255))
            self.homeInterface.label_volumn.setTextColor(QColor(255,255,255))
        elif theme == Theme.LIGHT:
            self.homeInterface.label_book.setTextColor(QColor(0,0,0))
            self.homeInterface.label_volumn.setTextColor(QColor(0,0,0))


    
if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    setTheme(Theme.DARK)
    setThemeColor('#FF7233')
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
