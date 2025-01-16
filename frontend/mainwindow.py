# coding:utf-8
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (setTheme, Theme, Theme, setTheme, Theme, FluentWindow, NavigationItemPosition, qconfig, SplashScreen)

from qfluentwidgets import FluentIcon as FIF
import base64
from resource.logo import logo_base64
from resource.logo_big import logo_big_base64
from backend.bilinovel.bilinovel_router import *

from frontend.cfg_utils import *
from frontend.gui_utils import font_label
from frontend.bilinovel_gui import NovelWidget
from frontend.bilimanga_gui import MangaWidget
from frontend.setting import SettingWidget
        
class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(logo_big_base64))
        # create splash screen
        self.splashScreen = SplashScreen(QIcon(pixmap), self)
        self.splashScreen.setIconSize(QSize(400, 400))
        self.splashScreen.raise_()

        initialize_db()
        self.out_path = read_config_dict("download_path")
        split_str = '--------------------------------\n    '
        self.novel_text = f'使用说明（必看）：\n{split_str}1. https://www.linovelib.com，输入书号以及下载的卷号，例如网址是https://www.linovelib.com/novel/2704.html，则书号输入2704。若不确定卷号，可以只输入书号，点击确定会返回书籍卷名称和对应的卷号。\n{split_str}3.要下载编号[2]对应卷，则卷号输入2。想下载多卷比如[1]至[3]对应卷，则卷号输入1-3或1,2,3（英文逗号分隔，编号可以不连续）。'
        self.manga_text = f'使用说明（必看）：\n{split_str}1.https://www.bilicomic.net，输入漫画号以及下载的卷号，例如网址是https://www.bilimanga.net/detail/498.html，则漫号输入498。若不确定卷号，可以只输入漫号，点击确定会返回漫画卷名称和对应的卷号。\n{split_str}3.要下载编[2]对应卷，则卷号输入2。想下载多卷比如[1]至[3]对应卷，则卷号输入1-3或1,2,3（英文逗号分隔，编号可以不连续）。'
        self.interval = read_config_dict('interval')
        self.NovelInterface = NovelWidget('Novel Interface', self)
        self.MangaInterface = MangaWidget('Manga Interface', self)
        self.settingInterface = SettingWidget('Setting Interface', self)
        self.initNavigation()
        self.initWindow()
        QTimer.singleShot(50, lambda: self.set_theme(read_config_dict('theme')))
        QTimer.singleShot(2000, lambda: self.splashScreen.close())
        
    def initNavigation(self):
        self.addSubInterface(self.NovelInterface, FIF.BOOK_SHELF, '哔哩轻小说')
        self.addSubInterface(self.MangaInterface, FIF.PHOTO, '哔哩漫画')
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(700, 460)
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(logo_base64))
       
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle('哔哩轻小说漫画EPUB下载器')
        self.setFont(font_label)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
    
    def set_theme(self, mode=None):
        if mode=='Light':
            setTheme(Theme.LIGHT)
        elif mode=='Dark':
            setTheme(Theme.DARK)
        elif mode== 'Auto':
            setTheme(Theme.AUTO)
        theme = qconfig.theme
        if theme == Theme.DARK:
            self.NovelInterface.label_book.setTextColor(QColor(255,255,255))
            self.NovelInterface.label_volumn.setTextColor(QColor(255,255,255))
            self.MangaInterface.label_book.setTextColor(QColor(255,255,255))
            self.MangaInterface.label_volumn.setTextColor(QColor(255,255,255))
        elif theme == Theme.LIGHT:
            self.NovelInterface.label_book.setTextColor(QColor(0,0,0))
            self.NovelInterface.label_volumn.setTextColor(QColor(0,0,0))
            self.MangaInterface.label_book.setTextColor(QColor(0,0,0))
            self.MangaInterface.label_volumn.setTextColor(QColor(0,0,0))