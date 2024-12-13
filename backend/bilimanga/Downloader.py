#!/usr/bin/python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import time  # 时间相关操作
import os
from rich.progress import track as tqdm
from backend.bilinovel.utils import *
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from DrissionPage import Chromium, ChromiumOptions
import tempfile
import shutil
from .utils import convert_avif_to_jpg

lock = threading.RLock()

class Downloader(object):
    def __init__(self, root_path, head='https://www.bilimanga.net', book_no='0000', volume_no=1, interval=0, color_page = 0):

        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'referer': head, 'cookie':'night=1'}

        self.url_head = head
        self.interval = float(interval)/1000
        self.color_page = int(color_page)
        self.main_page = f'{self.url_head}/detail/{book_no}.html'
        self.cata_page = f'{self.url_head}/read/{book_no}/catalog'
        self.read_tool_page = f'{self.url_head}/themes/zhmb/js/readtool.js'
        self.color_page_name = '彩页'
        self.html_buffer = dict()
        

        path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'  # 请改为你电脑内Chrome可执行文件路径
        co = ChromiumOptions().set_browser_path(path)
        self.tab = Chromium(co).latest_tab
        
        main_html = self.get_html(self.main_page)
        self.get_meta_data(main_html)
            
        self.img_url_map = dict()
        self.volume_no = volume_no

        self.epub_path = root_path
        self.comic_path = os.path.join(self.epub_path,  check_chars(self.title) + '_' + str(self.volume_no))
        self.temp_path_io = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_path_io.name
        
        self.missing_last_chap_list = []
        self.is_color_page = True
        self.page_url_map = dict()
        self.ignore_urls = []
        self.url_buffer = []
        self.max_thread_num = 8
        self.pool = ThreadPoolExecutor(1)
        
    # 获取html文档内容
    def get_html(self, url, is_gbk=False):
        
        while True:
            self.tab.get(url)
            # time.sleep(5) 
            # time.sleep(500)
            req = self.tab.html
            while '<title>Access denied | www.linovelib.com used Cloudflare to restrict access</title>' in req:
                print('下载频繁，触发反爬，5秒后重试....')
                time.sleep(5)
                self.tab.get(url)
                req = self.tab.html
            if is_gbk:
                req.encoding = 'GBK'       #这里是网页的编码转换，根据网页的实际需要进行修改，经测试这个编码没有问题
            break
        return req
    
    def get_meta_data(self, main_html):
        bf = BeautifulSoup(main_html, 'html.parser')
        self.title = bf.find('h1', class_='book-title').text
        self.author = bf.find('span', class_='authorname').text 
        self.brief = bf.find('section', id='bookSummary').text.replace('\n', '')

        book_meta = bf.find('span', class_='tag-small-group')

        self.tag_list = []
        if book_meta:
            for a_tag in book_meta.find_all('a'):
                self.tag_list.append(a_tag.text)
        
    def make_folder(self):
        os.makedirs(self.comic_path, exist_ok=True)

        self.text_path = os.path.join(self.comic_path, 'OEBPS/Text')
        os.makedirs(self.text_path, exist_ok=True)

        self.img_path = os.path.join(self.comic_path,  'OEBPS/Images')
        os.makedirs(self.img_path, exist_ok=True)
    
    def get_index_url(self):
        self.volume = {}
        self.volume['chap_urls'] = []
        self.volume['chap_names'] = []
        chap_html_list = self.get_chap_list(is_print=False)
        if len(chap_html_list)<self.volume_no:
            print('输入卷号超过实际卷数！')
            return False
        volume_array = self.volume_no - 1
        chap_html = chap_html_list[volume_array]

        self.volume['book_name'] = chap_html.find('h3').text
        chap_list = chap_html.find_all('li', {'class', 'chapter-li jsChapter'})
        for chap_html in chap_list:
            chap_name = chap_html.find('span').text
            self.volume['chap_names'].append(chap_name)
            self.volume['chap_urls'].append(self.url_head + chap_html.find('a').get('href'))
        return True
        
    def get_chap_list(self, is_print=True):
        cata_html = self.get_html(self.cata_page, is_gbk=False)
        bf = BeautifulSoup(cata_html, 'html.parser')
        chap_html_list = bf.find_all('div', class_='catalog-volume')
        if is_print:
            for chap_no, chap_html in enumerate(chap_html_list):
                print(f'[{chap_no+1}]', chap_html.find('h3').text)
        else:
            return chap_html_list

    def get_manga(self, is_gui=False, signal=None):
        for chap_no, (chap_name, chap_url) in enumerate(zip(self.volume['chap_names'], self.volume['chap_urls'])):
            print(chap_name)
            chap_html = self.get_html(chap_url)
            
            is_color_page = (self.color_page>0 and chap_no==0)
            self.get_chap_image(chap_no, chap_name, is_gui, signal, is_color_page)
            is_fix_next_chap_url = (chap_name in self.missing_last_chap_list)
            if is_fix_next_chap_url: 
                next_chap_url = self.url_head + re.search(r"url_next:\'(.*?)\',", chap_html).group(1)
                self.volume['chap_urls'][chap_no+1] = next_chap_url #正向修复
        if self.color_page>1:   #彩页数量大于1的情况下添加彩页， 否则当没有彩页处理
            self.volume['chap_names'] = [self.color_page_name] + self.volume['chap_names']
        self.temp_path_io.cleanup()
        
            
    def get_chap_image(self, chap_no, chap_name, is_gui=False, signal=None, is_color_page=False):
        save_path = os.path.join(self.comic_path, chap_name)
        os.makedirs(save_path, exist_ok=True)
        chap_html = BeautifulSoup(self.tab.html, 'html.parser')
        img_elements = chap_html.find_all('img', class_='imagecontent')
        img_url_list = [img_element.get('data-src') for img_element in img_elements]
        # self.pool.submit(self.scroll_back)
        if chap_no==0:
            self.get_single_image(img_url_list[0], self.comic_path, "cover.avif") #默认第一张为彩页
        if is_color_page:
            if self.color_page > 1: #彩页数量大于1的情况下添加彩页， 否则当没有彩页处理
                img_url_list_color = img_url_list[1:self.color_page]
                save_path_color = os.path.join(self.comic_path, self.color_page_name) 
                os.makedirs(save_path_color, exist_ok=True)
                if len(os.listdir(save_path_color))!=len(img_url_list_color):
                    self.clear_dir(save_path_color)
                    for i, img_url in enumerate(img_url_list_color):
                        self.get_single_image(img_url, save_path_color, f"{str(i).zfill(3)}.avif")
            img_url_list = img_url_list[self.color_page:]
        
        if is_gui:
            len_iter = len(img_elements)
            signal.emit('start')
            if len(os.listdir(save_path))!=len(img_url_list):
                self.clear_dir(save_path)
                for i, img_url in enumerate(img_url_list):
                    self.get_single_image(img_url, save_path, f"{str(i).zfill(3)}.avif")
                    signal.emit(int(100*(i+1)/len_iter))
            signal.emit('end')
        else:
            if len(os.listdir(save_path))!=len(img_url_list):
                self.clear_dir(save_path)
                for i, img_url in enumerate(tqdm(img_url_list)):
                    self.get_single_image(img_url, save_path, f"{str(i).zfill(3)}.avif")
            
    def get_single_image(self, img_url, save_path, save_name):
        img_element = self.tab.ele(f'@@tag()=img@@data-src={img_url}')
        while img_element.attrs['class'] == 'imagecontent lazyload':
            self.tab.scroll.to_see(img_element)
            time.sleep(0.1)
            img_element = self.tab.ele(f'@@tag()=img@@data-src={img_url}')
        try:
            img_element.save(self.temp_path, save_name, rename=False)
            convert_avif_to_jpg(os.path.join(self.temp_path, save_name), os.path.join(save_path, save_name.replace('.avif', '.jpg')))
            os.remove(os.path.join(self.temp_path, save_name))
        except Exception as error:
            print(error)
            self.tab.refresh()
            self.get_single_image(img_url, save_path, save_name)

    def clear_dir(self, path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

        

    def scroll_back(self):
        while True:
            chap_html = BeautifulSoup(self.tab.html, 'html.parser')
            unload_bf = chap_html.find('img', class_='imagecontent lazyload')
            if unload_bf is None:
                break
            else:
                self.tab.scroll.to_see(self.tab.ele('@@tag()=img@@class=imagecontent lazyload'))
            # time.sleep(0.4)

    
    def check_url(self, url):#当检测有问题返回True
        return ('javascript' in url or 'cid' in url)   

    def get_prev_url(self, chap_no): #获取前一个章节的链接
        content_html = self.get_html(self.volume['chap_urls'][chap_no], is_gbk=False)
        next_url = self.url_head + re.search(r"url_previous:\'(.*?)\',", content_html).group(1)
        return next_url
    
    def prev_fix_url(self, chap_no, chap_num):  #反向递归修复缺失链接（后修复前），若成功修复返回True，否则返回False 
        if chap_no==chap_num-1: #最后一个章节直接选择不修复 返回False
            return False
        elif self.check_url(self.volume['chap_urls'][chap_no+1]):
            if self.prev_fix_url(chap_no+1, chap_num):
                self.volume['chap_urls'][chap_no] = self.get_prev_url(chap_no+1)
                return True
            else:
                return False
        else:
            self.volume['chap_urls'][chap_no] = self.get_prev_url(chap_no+1)
            return True
        
    def check_volume(self, is_gui=False, signal=None, editline=None):
        chap_names = self.volume['chap_names']
        chap_num = len(self.volume['chap_names'])
        for chap_no, url in enumerate(self.volume['chap_urls']):
            if self.check_url(url):
                if not self.prev_fix_url(chap_no, chap_num): #先尝试反向递归修复
                    if chap_no == 0:    #第一个章节都反向修复失败 说明后面章节全部缺失，只能手动输入第一个章节，保证第一个章节一定有效
                        self.volume['chap_urls'][0] = self.hand_in_url(chap_names[chap_no], is_gui, signal, editline)
                    else:   #其余章节反向修复失败 默认使用正向修复 
                        self.missing_last_chap_list.append(chap_names[chap_no-1])


    def hand_in_msg(self, error_msg='', is_gui=False, signal=None, editline=None):
        if is_gui:
            print(error_msg)
            signal.emit('hang')
            time.sleep(1)
            while not editline.isHidden():
                time.sleep(1)
            content = editline.text()
            editline.clear()
        else:
            content = input(error_msg)
        return content
            
    def hand_in_url(self, chap_name, is_gui=False, signal=None, editline=None):
        error_msg = f'章节\"{chap_name}\"连接失效，请手动输入该章节链接(手机版“{self.url_head}”开头的链接):'
        return self.hand_in_msg(error_msg, is_gui, signal, editline)