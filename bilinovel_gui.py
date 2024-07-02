# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QRegExp
from PyQt5.QtGui import QIcon, QFont, QTextCursor, QPixmap, QColor,QRegExpValidator
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QFileDialog
from qfluentwidgets import (setTheme, Theme, PushSettingCard, SettingCardGroup, ExpandLayout, TextEdit, ImageLabel, LineEdit, PushButton, Theme, ProgressRing, setTheme, Theme, OptionsSettingCard, OptionsConfigItem, OptionsValidator, FluentWindow, SubtitleLabel, NavigationItemPosition, setThemeColor, qconfig, EditableComboBox, BoolValidator, SwitchSettingCard, ComboBoxSettingCard)
from qfluentwidgets import FluentIcon as FIF
import sys
import base64
import shutil
from resource.logo import logo_base64
from resource.book import book_base64
from bilinovel import *
import configparser
from output_format import OutputFormat, is_valid_format, find_format

font_label = QFont('微软雅黑', 18)
font_msg = QFont('微软雅黑', 11)

class MainThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        
    def run(self):
        self.parent.clear_signal.emit('')
        try:
            book_no = self.parent.editline_book.text()
            volumn_no = self.parent.editline_volumn.text()
            downloader_router(
                self.parent.parent.out_path,
                book_no, volumn_no,
                True,
                self.parent.hang_signal,
                self.parent.progressring_signal,
                self.parent.cover_signal,
                self.parent.editline_hang,
                self.parent.parent.to_traditional_chinese,
                self.parent.parent.confirm_no_img,
                self.parent.parent.output_file_type
            )
            self.parent.end_signal.emit('')
        except Exception as e:
            self.parent.end_signal.emit('')
            print('错误，请检查网络情况或确认输入是否正确')
            print('错误信息：')
            print(e)
    def terminate(self) -> None:
        result = super().terminate()
        return result

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

        self.outputFileTypeMode = OptionsConfigItem(
            None, "outputFileTypeMode", find_format(self.parent.output_file_type), OptionsValidator(OutputFormat))

        self.toTraditionalChineseMode = OptionsConfigItem(
        None, "ToTraditionalChineseMode", self.parent.to_traditional_chinese, BoolValidator())

        self.confirmNoImgMode = OptionsConfigItem(
        None, "ConfirmNoImgMode", self.parent.confirm_no_img, BoolValidator())

        self.threadMode = OptionsConfigItem(
        None, "ThreadMode", True, BoolValidator())

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

        self.output_file_type_card = ComboBoxSettingCard(
            self.outputFileTypeMode,
            FIF.SAVE_AS,
            self.tr('輸出檔案'),
            self.tr('檔案類型'),
            texts=[self.tr(format_name.value) for format_name in OutputFormat],
            parent=self.parent
        )

        self.language_card = OptionsSettingCard(
            self.toTraditionalChineseMode,
            FIF.LANGUAGE,
            self.tr('輸出語言'),
            self.tr("更改語言"),
            texts=[
                self.tr('繁體中文'), self.tr('简体中文')
            ],
            parent=self.parent
        )

        self.confirm_no_img_card = SwitchSettingCard(
            FIF.ADD_TO,
            self.tr('插图页面不存在时'),
            self.tr("手动新增插图页面"),
            self.confirmNoImgMode,
            self.parent
        )

        self.setting_group.addSettingCard(self.download_path_card)
        self.setting_group.addSettingCard(self.theme_card)
        self.setting_group.addSettingCard(self.output_file_type_card)
        self.setting_group.addSettingCard(self.language_card)
        self.setting_group.addSettingCard(self.confirm_no_img_card)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 10, 20, 0)
        self.expandLayout.addWidget(self.setting_group)

        self.download_path_card.clicked.connect(self.download_path_changed)
        self.theme_card.optionChanged.connect(self.theme_changed)
        self.outputFileTypeMode.valueChanged.connect(self.output_file_type_changed)
        self.language_card.optionChanged.connect(self.language_changed)
        self.confirm_no_img_card.checkedChanged.connect(self.confirm_no_img_changed)

    def download_path_changed(self):
        """ download folder card clicked slot """
        self.parent.out_path = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), self.parent.out_path)
        self.parent.save_config_out_path(self.parent.out_path)
        self.download_path_card.contentLabel.setText(self.parent.out_path)
    
    def theme_changed(self):
        theme_name = self.theme_card.choiceLabel.text()
        self.parent.set_theme(theme_name)
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def output_file_type_changed(self):
        self.parent.output_file_type = self.outputFileTypeMode.value.value
        self.parent.save_config_output_file_type(self.parent.output_file_type)
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def language_changed(self):
        language = self.language_card.choiceLabel.text()
        if language=="繁體中文":
            self.parent.to_traditional_chinese = True
            print("輸出設定成繁體中文，若需更改請至設定頁面")
        else:
            self.parent.to_traditional_chinese = False
            print("输出设定成简体中文，若需更改请至设定页面")
        self.parent.save_config_to_traditional_chinese(self.parent.to_traditional_chinese)
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def confirm_no_img_changed(self):
        confirm_no_img = self.confirm_no_img_card.isChecked()
        if confirm_no_img:
            self.parent.confirm_no_img = True
        else:
            self.parent.confirm_no_img = False
        self.parent.save_config_confirm_no_img(self.parent.confirm_no_img)
        if os.path.exists('./config'):
            shutil.rmtree('./config')

class HomeWidget(QFrame):

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
        
        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)
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
        
        
    

class Window(FluentWindow):
    def __init__(self):
        super().__init__()

        self.config_path = os.path.join(os.path.expanduser('~'), '.bilinovel.conf')
        self.out_path = self.get_config_out_path()
        self.to_traditional_chinese = self.get_config_to_traditional_chinese()
        self.confirm_no_img = self.get_config_confirm_no_img()
        self.output_file_type = self.get_config_output_file_type()
        self.head = 'https://www.linovelib.com'
        split_str = '**************************************\n    '
        self.welcome_text = f'使用说明（共5条，记得下拉）：\n{split_str}1.哔哩轻小说{self.head}，根据书籍网址输入书号以及下载的卷号，书号最多输入4位阿拉伯数字。\n{split_str}2.例如小说网址是{self.head}/novel/2704.html，则书号输入2704。\n{split_str}3.要查询书籍卷号卷名等信息，则可以只输入书号不输入卷号，点击确定会返回书籍卷名称和对应的卷号。\n{split_str}4.根据上一步返回的信息确定自己想下载的卷号，要下载编号[2]对应卷，则卷号输入2。想下载多卷比如[1]至[3]对应卷，则卷号输入1-3或1,2,3（英文逗号分隔，编号也可以不连续）并点击确定。\n{split_str}5.若需更改.epub 输出语言请至设定页面，目前输出为{"繁體中文" if self.to_traditional_chinese else "简体中文"}。\n'
        self.homeInterface = HomeWidget('Home Interface', self)
        self.settingInterface = SettingWidget('Setting Interface', self)
        self.initNavigation()
        self.initWindow()

    def get_config_out_path(self):
        """
        get out_path variable from config file, else use default
        
            Returns:
                out_path (str)
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        try:
            out_path = config.get('Settings', 'out_path')
            assert(os.path.isdir(out_path))
        except:
            if not config.has_section('Settings'):
                config.add_section('Settings')
            out_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            config.set('Settings', 'out_path', out_path)
            with open(self.config_path, "w") as configfile:
                config.write(configfile)
        return out_path
    
    def get_config_output_file_type(self):
        """
        get output_file_type variable from config file, else use default
        
            Returns:
                output_file_type (str)
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        try:
            output_file_type = config.get('Settings', 'output_file_type')
            assert(is_valid_format(output_file_type))
        except:
            if not config.has_section('Settings'):
                config.add_section('Settings')
            output_file_type = "epub"
            config.set('Settings', 'output_file_type', output_file_type)
            with open(self.config_path, "w") as configfile:
                config.write(configfile)
        return output_file_type
    
    def get_config_to_traditional_chinese(self):
        """
        get to_traditional_chinese variable from config file, else use default
        
            Returns:
                to_traditional_chinese (bool)
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        try:
            to_traditional_chinese = config.getboolean('Settings', 'to_traditional_chinese')
        except:
            if not config.has_section('Settings'):
                config.add_section('Settings')
            to_traditional_chinese = False
            config.set('Settings', 'to_traditional_chinese', 'false')
            with open(self.config_path, "w") as configfile:
                config.write(configfile)
        return to_traditional_chinese
    
    def get_config_confirm_no_img(self):
        """
        get confirm_no_img variable from config file, else use default
        
            Returns:
                confirm_no_img (bool)
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        try:
            confirm_no_img = config.getboolean('Settings', 'confirm_no_img')
        except:
            if not config.has_section('Settings'):
                config.add_section('Settings')
            confirm_no_img = True
            config.set('Settings', 'confirm_no_img', 'true')
            with open(self.config_path, "w") as configfile:
                config.write(configfile)
        return confirm_no_img

    def save_config_to_traditional_chinese(self, to_traditional_chinese):
        """
        save to_traditional_chinese variable to config file
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if not config.has_section('Settings'):
            config.add_section('Settings')

        if to_traditional_chinese:
            config.set('Settings', 'to_traditional_chinese', 'true')
        else:
            config.set('Settings', 'to_traditional_chinese', 'false')
        
        with open(self.config_path, "w") as configfile:
            config.write(configfile)

    def save_config_confirm_no_img(self, confirm_no_img):
        """
        save confirm_no_img variable to config file
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if not config.has_section('Settings'):
            config.add_section('Settings')

        if confirm_no_img:
            config.set('Settings', 'confirm_no_img', 'true')
        else:
            config.set('Settings', 'confirm_no_img', 'false')
        
        with open(self.config_path, "w") as configfile:
            config.write(configfile)

    def save_config_out_path(self, out_path):
        """
        save out_path variable to config file
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if not config.has_section('Settings'):
            config.add_section('Settings')

        if os.path.isdir(out_path):
            config.set('Settings', 'out_path', out_path)
        else:
            print(f"{out_path} is not a directory. Not saving into {self.config_path}.")
        
        with open(self.config_path, "w") as configfile:
            config.write(configfile)

    def save_config_output_file_type(self, output_file_type):
        """
        save output_file_type variable to config file
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if not config.has_section('Settings'):
            config.add_section('Settings')

        if is_valid_format(output_file_type):
            config.set('Settings', 'output_file_type', output_file_type)
        else:
            print(f"{output_file_type} is not a valid format. Not saving into {self.config_path}.")
        
        with open(self.config_path, "w") as configfile:
            config.write(configfile)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '主界面')
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(700, 460)
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(logo_base64))
        self.setWindowIcon(QIcon(pixmap))
        self.setWindowTitle('哔哩轻小说EPUB下载器')
        self.setFont(font_label)

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
