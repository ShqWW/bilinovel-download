# coding:utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QWidget
from qfluentwidgets import (Theme, PushSettingCard, SettingCardGroup, ExpandLayout, Theme, Theme, OptionsSettingCard, OptionsConfigItem, OptionsValidator, RangeSettingCard, ScrollArea, RangeValidator, RangeConfigItem)

from qfluentwidgets import FluentIcon as FIF
from .cfg_utils import read_config_dict, write_config_dict
import os
import shutil


class SettingWidget(ScrollArea):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.parent = parent
        self.setting_group = SettingCardGroup(self.tr("设置"), self.scrollWidget)
        
        self.download_path_card = PushSettingCard(
            self.tr('选择文件夹'),
            FIF.DOWNLOAD,
            self.tr("下载目录"),
            self.parent.out_path,
            self.setting_group
        )

        theme_name = read_config_dict('theme')
        if theme_name == 'Light':
            self.themeMode = OptionsConfigItem(
        None, "ThemeMode", Theme.LIGHT, OptionsValidator(Theme), None)
        elif theme_name == 'Dark':
            self.themeMode = OptionsConfigItem(
        None, "ThemeMode", Theme.DARK, OptionsValidator(Theme), None)
        else:
            self.themeMode = OptionsConfigItem(
        None, "ThemeMode", Theme.AUTO, OptionsValidator(Theme), None)

        self.interval_card = RangeSettingCard(
            RangeConfigItem("interval", "时间间隔", int(read_config_dict("interval")), RangeValidator(0, 8000)),
            FIF.DATE_TIME,
            self.tr('下载时间间隔(毫秒)'),
            self.tr('如果页面频繁陷入超时，建议适当延长下载间隔'),
            self.setting_group
        )

        self.thread_card = RangeSettingCard(
            RangeConfigItem("thread", "下载线程数量", int(read_config_dict("numthread")), RangeValidator(1, 10)),
            FIF.SPEED_HIGH,
            self.tr('小说插画下载线程数量'),
            self.tr('适当增加充分利用带宽,但不要太高'),
            self.setting_group
        ) 

        self.theme_card = OptionsSettingCard(
            self.themeMode,
            FIF.BRUSH,
            self.tr('应用主题'),
            self.tr("更改外观"),
            texts=[
                self.tr('亮'), self.tr('暗'),
                self.tr('跟随系统')
            ],
            parent=self.setting_group
        )
        

        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 10, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface2')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        qss = '''
                SettingInterface, #scrollWidget {
                    background-color: transparent;
                }

                QScrollArea {
                    border: none;
                    background-color: transparent;
                }

                QLabel#settingLabel {
                    font: 33px 'Microsoft YaHei Light';
                    background-color: transparent;
                    color: white;
                }

                '''
        
        self.setStyleSheet(qss)

        self.setting_group.addSettingCard(self.download_path_card)
        self.setting_group.addSettingCard(self.interval_card)
        self.setting_group.addSettingCard(self.thread_card)
        self.setting_group.addSettingCard(self.theme_card)
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(20, 10, 20, 0)
        self.expandLayout.addWidget(self.setting_group)   

        self.download_path_card.clicked.connect(self.download_path_changed)
        self.theme_card.optionChanged.connect(self.theme_changed)
        self.interval_card.valueChanged.connect(self.interval_changed)
        self.thread_card.valueChanged.connect(self.thread_changed)


    def download_path_changed(self):
        """ download folder card clicked slot """
        new_path = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), self.parent.out_path)
        if new_path:
            write_config_dict("download_path", new_path)
        self.download_path_card.contentLabel.setText(read_config_dict("download_path"))
        
    
    def theme_changed(self):
        theme_name = self.theme_card.choiceLabel.text()
        if theme_name == '亮':
            theme_mode = 'Light' 
        elif theme_name == '暗':
            theme_mode = 'Dark' 
        elif theme_name == '跟随系统':
            theme_mode = 'Auto' 
        write_config_dict("theme", theme_mode)
        self.parent.set_theme(read_config_dict("theme"))
        if os.path.exists('./config'):
            shutil.rmtree('./config')

    def interval_changed(self):
        interval = self.interval_card.valueLabel.text()
        write_config_dict("interval", interval)

    def thread_changed(self):
        num_thread = self.thread_card.valueLabel.text()
        write_config_dict("numthread", num_thread)