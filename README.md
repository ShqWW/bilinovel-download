
<div align="center">
  <img src="resource/logo_big.png" width="300" style="margin-right: 3000px;"/> 
</div>

<h1 align="center">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;EPUB下载器
</h1>





[哔哩轻小说](https://www.bilinovel.com)(linovelib)网站小说下载，支持多线程和批量下载，并转化为EPUB格式，黑白与彩色插图、目录与封面自动排版，支持多种阅读器。

有建议或bug可以提issue，也可以加QQ群：563072544

图形界面使用[PyQt-Fluent-Widgets](https://pyqt-fluent-widgets.readthedocs.io/en/latest/index.html)界面编写，fluent design风格，支持亮暗两种主题。

[release](https://github.com/ShqWW/bilinovel-download/releases/tag/downloader)页面发布了已经打包好的exe可执行程序(系统最低要求Windows 10)。

界面样例：
<div align="center">
  <img src="resource/example1.png" width="400"/>
  <img src="resource/example2.png" width="400"/>
</div>

PS：暂不支持漫画的排版，后续会开新坑专门支持漫画

## 使用前安装需要的包
```
pip install -r requirements.txt -i https://pypi.org/simple/
```
## 使用命令行模式运行(无需安装图形界面库，支持Linux):
```
python bilinovel.py
```

## 使用图形界面运行:
```
python bilinovel_gui.py
```

## 使用pyinstaller打包:
```
pip install pyinstaller
```
```
pyinstaller -F -w -i .\resource\logo.png --paths=C:\Users\haoru\bilinovel-download .\bilinovel_gui.py --clean
```


## EPUB书籍编辑和管理软件推荐：
1. [Sigil](https://sigil-ebook.com/)
2. [Calibre](https://www.calibre-ebook.com/)

