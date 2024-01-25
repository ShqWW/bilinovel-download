#!/usr/bin/python
# -*- coding:utf-8 -*-

import requests  # 用来抓取网页的html源码
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import time  # 时间相关操作
import os
from rich.progress import track as tqdm
from utils import *
import zipfile
import shutil
import re
import pickle
from PIL import Image
import time
import threading
from concurrent.futures import ThreadPoolExecutor, wait
import pickle
from selenium import webdriver
from selenium.webdriver.edge.options import Options

lock = threading.RLock()

class Editer(object):
    def __init__(self, root_path, head='https://www.linovelib.com', book_no='0000', volume_no=1):
        
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'referer': head}

        self.url_head = head
        options = Options()

        self.driver = webdriver.Edge(options = options)
        self.main_page = f'{self.url_head}/novel/{book_no}.html'
        self.cata_page = f'{self.url_head}/novel/{book_no}/catalog'
        self.read_tool_page = f'{self.url_head}/themes/zhmb/js/readtool.js'
        self.color_chap_name = '插图'
        self.color_page_name = '彩页'
        self.html_buffer = dict()
        
        main_html = self.get_html(self.main_page)
        bf = BeautifulSoup(main_html, 'html.parser')
        self.title = bf.find('meta', {"property": "og:novel:book_name"})['content']
        self.author = bf.find('meta', {"property": "og:novel:author"})['content']
        try:
            self.cover_url = re.search(r'src=\"(.*?)\"', str(bf.find('div', {"class": "book-img fl"}))).group(1)
        except:
            self.cover_url = 'cid'
            
        self.img_url_map = dict()
        self.volume_no = volume_no

        self.epub_path = root_path
        self.temp_path = check_chars(os.path.join(self.epub_path,  'temp_'+ self.title + '_' + str(self.volume_no)))
    
        self.missing_last_chap_list = []
        self.is_color_page = True
        self.page_url_map = dict()
        self.ignore_urls = []
        self.url_buffer = []
        self.max_thread_num = 8
        self.pool = ThreadPoolExecutor(self.max_thread_num)
        
    # 获取html文档内容
    def get_html(self, url, is_gbk=False):
        while True:
            time.sleep(0.5)
            self.driver.get(url)
            req = self.driver.page_source
            while '<title>Access denied | www.linovelib.com used Cloudflare to restrict access</title>' in req:
                time.sleep(5)
                self.driver.get(url)
                req = self.driver.page_source
            if is_gbk:
                req.encoding = 'GBK'       #这里是网页的编码转换，根据网页的实际需要进行修改，经测试这个编码没有问题
            break
        return req
    
    def get_html_img(self, url, is_buffer=False):
        if is_buffer:
            while not url in self.html_buffer.keys():
                time.sleep(0.1) 
        if url in self.html_buffer.keys():
            return self.html_buffer[url]
        while True:
            try:
                req=requests.get(url, headers=self.header)
                break
            except Exception as e:
                pass
        lock.acquire()
        self.html_buffer[url] = req.content
        lock.release()
        return req.content
    
    # def get_secret_map(self):
    #     with open('secret_map.cfg', 'rb') as f:
    #         self.secret_map = pickle.load(f)
        
    def make_folder(self):
        os.makedirs(self.temp_path, exist_ok=True)

        self.text_path = os.path.join(self.temp_path, 'OEBPS/Text')
        os.makedirs(self.text_path, exist_ok=True)

        self.img_path = os.path.join(self.temp_path,  'OEBPS/Images')
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

        self.volume['book_name'] = chap_html.find('h2', {'class': 'v-line'}).text
        chap_list = chap_html.find_all('li', {'class', 'col-4'})
        for chap_html in chap_list:
            self.volume['chap_names'].append(chap_html.text)
            self.volume['chap_urls'].append(self.url_head + chap_html.find('a').get('href'))
        return True
        
    def get_chap_list(self, is_print=True):
        cata_html = self.get_html(self.cata_page, is_gbk=False)
        bf = BeautifulSoup(cata_html, 'html.parser')
        chap_html_list = bf.find_all('div', {'class', 'volume clearfix'})
        if is_print:
            for chap_no, chap_html in enumerate(chap_html_list):
                print(f'[{chap_no+1}]', chap_html.find('h2', {'class': 'v-line'}).text)
            return
        else:
            return chap_html_list


    def get_page_text(self, content_html):
        bf = BeautifulSoup(content_html, 'html.parser')
        text_with_head = bf.find('div', {'id': 'TextContent', 'class': 'read-content'}) 
        text_html = str(text_with_head)
        img_urlre_list = re.findall(r"<img .*?>", text_html)
        for img_urlre in img_urlre_list:
            img_url_full = re.search(r'.[a-zA-Z]{3}/(.*?).(jpg|png|jpeg)', img_urlre)
            img_url_name = img_url_full.group(1)
            img_url_tail = img_url_full.group(0).split('.')[-1]
            img_url = f'https://img3.readpai.com/{img_url_name}.{img_url_tail}'

            text_html = text_html.replace('<br/>\n' + img_urlre +'\n<br/>', img_urlre)
            if not img_url in self.img_url_map:
                self.img_url_map[img_url] = str(len(self.img_url_map)).zfill(2)
            img_symbol = f'<p>[img:{self.img_url_map[img_url]}]</p>'
            if '00' in img_symbol:
                text_html = text_html.replace(img_urlre, '')  #默认第一张为封面图片 不写入彩页
            else:
                text_html = text_html.replace(img_urlre, img_symbol)
                symbol_index = text_html.index(img_symbol)
                if text_html[symbol_index-1] != '\n':
                    text_html = text_html[:symbol_index] + '\n' + text_html[symbol_index:]
        text = BeautifulSoup(text_html, 'html.parser').get_text()
        return text
    
    def get_chap_text(self, url, chap_name, return_next_chapter=False):
        text_chap = ''
        page_no = 1 
        url_ori = url
        next_chap_url = None
        while True:
            if page_no == 1:
                str_out = chap_name
            else:
                str_out = f'    正在下载第{page_no}页......'
            print(str_out)
            content_html = self.get_html(url, is_gbk=False)
            text = self.get_page_text(content_html)
            text_chap += text
            url_new = url_ori.replace('.html', '_{}.html'.format(page_no+1))[len(self.url_head):]
            if url_new in content_html:
                page_no += 1
                url = self.url_head + url_new
            else:
                if return_next_chapter:
                    next_chap_url = self.url_head + re.search(r'书签</a><a href="(.*?)">下一章</a>', content_html).group(1)
                break
        return text_chap, next_chap_url
    
    def get_text(self):
        self.make_folder()   
        img_strs = []   #记录后文中出现的所有图片位置
        text_no=0   #text_no正文章节编号(排除插图)   chap_no 是所有章节编号
        for chap_no, (chap_name, chap_url) in enumerate(zip(self.volume['chap_names'], self.volume['chap_urls'])):
            is_fix_next_chap_url = (chap_name in self.missing_last_chap_list)
            text, next_chap_url = self.get_chap_text(chap_url, chap_name, return_next_chapter=is_fix_next_chap_url)
            if is_fix_next_chap_url: 
                self.volume['chap_urls'][chap_no+1] = next_chap_url #正向修复
            if chap_name == self.color_chap_name:
                text_html_color = text2htmls(self.color_page_name, text)
            else:
                text_html = text2htmls(chap_name, text)
                textfile = self.text_path + f'/{str(text_no).zfill(2)}.xhtml'
                with open(textfile, 'w+', encoding='utf-8') as f:
                    f.writelines(text_html)
                for text_line in text_html:
                    img_str = re.search(r"<img(.*?)\/>", text_line)
                    if img_str is not None:
                        img_strs.append(img_str.group(0))
                text_no += 1
            
        # 将彩页中后文已经出现的图片删除，避免重复
        if self.is_color_page: #判断彩页是否存在
            text_html_color_new = []
            textfile = self.text_path + '/color.xhtml'
            for text_line in text_html_color: 
                is_save = True
                for img_str in img_strs:
                    if img_str in text_line:
                        is_save = False
                        break
                if is_save:
                   text_html_color_new.append(text_line) 
        
            with open(textfile, 'w+', encoding='utf-8') as f:
                f.writelines(text_html_color_new)
        

    def get_image(self, is_gui=False, signal=None):
        for url in self.img_url_map.keys():
            self.pool.submit(self.get_html_img, url)
        img_path = self.img_path
        if is_gui:
            len_iter = len(self.img_url_map.items())
            signal.emit('start')
            for i, (img_url, img_name) in enumerate(self.img_url_map.items()):
                content = self.get_html_img(img_url, is_buffer=True)
                with open(img_path+f'/{img_name}.jpg', 'wb') as f:
                    f.write(content) #写入二进制内容 
                signal.emit(int(100*(i+1)/len_iter))
            signal.emit('end')
        else:
            for img_url, img_name in tqdm(self.img_url_map.items()):
                content = self.get_html_img(img_url)
                with open(img_path+f'/{img_name}.jpg', 'wb') as f:
                    f.write(content) #写入二进制内容

    def get_cover(self, is_gui=False, signal=None):
        textfile = os.path.join(self.text_path, 'cover.xhtml')
        img_w, img_h = 300, 300
        try:
            imgfile = os.path.join(self.img_path, '00.jpg')
            img = Image.open(imgfile)
            img_w, img_h = img.size
            signal_msg = (imgfile, img_h, img_w)
            if is_gui:
                signal.emit(signal_msg)
        except Exception as e:
            print(e)
            print('没有封面图片，请自行用第三方EPUB编辑器手动添加封面')
        img_htmls = get_cover_html(img_w, img_h)
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(img_htmls)

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
        
         #没有检测到插图页，手动输入插图页标题
        if self.color_chap_name not in self.volume['chap_names']:
            self.color_chap_name = self.hand_in_color_page_name(is_gui, signal, editline)

        #没有彩页 但主页封面存在，将主页封面设为书籍封面 
        if self.color_chap_name=='' and (not self.check_url(self.cover_url)):  
            self.is_color_page = False
            self.img_url_map[self.cover_url] = str(len(self.img_url_map)).zfill(2)
            print('**************')
            print('提示：没有彩页，但主页封面存在，将使用主页的封面图片作为本卷图书封面')
            print('**************')
    
    def check_url(self, url):#当检测有问题返回True
        return ('javascript' in url or 'cid' in url)   
    
    def get_prev_url(self, chap_no): #获取前一个章节的链接
        content_html = self.get_html(self.volume['chap_urls'][chap_no], is_gbk=False)
        next_url = self.url_head + re.search(r'<div class="mlfy_page"><a href="(.*?)">上一章</a>', content_html).group(1)
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
    
    def hand_in_color_page_name(self, is_gui=False, signal=None, editline=None):
        if is_gui:
            error_msg = f'插图页面不存在，需要下拉选择插图页标题，若不需要插图页则保持本栏为空直接点确定：'
            editline.addItems(self.volume['chap_names'])
            editline.setCurrentIndex(-1)
        else:
            error_msg = f'插图页面不存在，需要手动输入插图页标题，若不需要插图页则不输入直接回车：'
        return self.hand_in_msg(error_msg, is_gui, signal, editline) 
    
    def get_toc(self):
        if self.is_color_page:
            ind = self.volume["chap_names"].index(self.color_chap_name)
            self.volume["chap_names"].pop(ind)
        toc_htmls = get_toc_html(self.title, self.volume["chap_names"])
        textfile = self.temp_path + '/OEBPS/toc.ncx'
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(toc_htmls)

    def get_content(self):
        num_chap = len(self.volume["chap_names"])
        num_img = len(os.listdir(self.img_path))
        content_htmls = get_content_html(self.title + '-' + self.volume['book_name'], self.author, num_chap, num_img, self.is_color_page)
        textfile = self.temp_path + '/OEBPS/content.opf'
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(content_htmls)

    def get_epub_head(self):
        mimetype = 'application/epub+zip'
        mimetypefile = self.temp_path + '/mimetype'
        with open(mimetypefile, 'w+', encoding='utf-8') as f:
            f.write(mimetype)
        metainf_folder = os.path.join(self.temp_path, 'META-INF')
        os.makedirs(metainf_folder, exist_ok=True)
        container = metainf_folder + '/container.xml'
        container_htmls = get_container_html()
        with open(container, 'w+', encoding='utf-8') as f:
            f.writelines(container_htmls)

    def get_epub(self):
        os.remove(os.path.join(self.temp_path, 'buffer.pkl'))
        epub_file = check_chars(self.epub_path + '/' + self.title + '-' + self.volume['book_name'] + '.epub')
        with zipfile.ZipFile(epub_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, _, filenames in os.walk(self.temp_path):
                fpath = dirpath.replace(self.temp_path,'') #这一句很重要，不replace的话，就从根目录开始复制
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    zf.write(os.path.join(dirpath, filename), fpath+filename)
        shutil.rmtree(self.temp_path)
        return epub_file
    
    # # 恢复函数，根据secret_map进行恢复
    # def restore_chars(self, text):
    #     restored_text = ""
    #     i = 0
    #     while i < len(text):
    #         char = text[i]
    #         if char in self.secret_map:
    #                 restored_text += self.secret_map[char]
    #         else:
    #                 restored_text += char
    #         i += 1
    #     return restored_text
    
    def buffer(self):
        filename = 'buffer.pkl'
        filepath = os.path.join(self.temp_path, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                self.volume, self.img_url_map = pickle.load(f)
                self.text_path = os.path.join(self.temp_path, 'OEBPS/Text')
                os.makedirs(self.text_path, exist_ok=True)
                self.img_path = os.path.join(self.temp_path,  'OEBPS/Images')
                os.makedirs(self.img_path, exist_ok=True)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump((self.volume ,self.img_url_map), f)
    
    def is_buffer(self):
        filename = 'buffer.pkl'
        filepath = os.path.join(self.temp_path, filename)
        return os.path.isfile(filepath)