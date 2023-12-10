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

lock = threading.RLock()

class Editer(object):
    def __init__(self, root_path, head='https://www.bilinovel.com', secret_map=None, book_no='0000', volume_no=1, multi_thread=False):
        
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'referer': head}

        self.url_head = head
        self.main_page = f'{self.url_head}/novel/{book_no}.html'
        self.cata_page = f'{self.url_head}/novel/{book_no}/catalog'
        self.read_tool_page = f'{self.url_head}/themes/zhmb/js/readtool.js'
        self.color_page_name = '插图'
        self.img_chap_name = '彩页'
        self.html_buffer = dict()

        
        if secret_map == None:
            self.get_secret_map()
        else:
            self.secret_map = secret_map

        main_html = self.get_html(self.main_page)
        bf = BeautifulSoup(main_html, 'html.parser')
        bf = bf.find('div', {'id': 'bookDetailWrapper'})
        self.title = bf.find('h2', {"class": "book-title"}).text
        self.author = bf.find('a').text
        try:
            self.cover_url = re.search(r'src=\"(.*?)\"', str(bf.find('img', {"class": "book-cover"}))).group(1)
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
        self.max_thread_num = 15
        self.pool = ThreadPoolExecutor(self.max_thread_num)
        self.multi_thread = multi_thread

        
        
    # 获取html文档内容
    def get_html(self, url, is_buffer=False, is_gbk=False):
        if is_buffer and url in self.url_buffer:
            while not url in self.html_buffer.keys():
                time.sleep(0.1) 
        if url in self.html_buffer.keys():
            # print(url)
            return self.html_buffer[url]
        while True:
            try:
                req = requests.get(url=url, headers=self.header)
                if is_gbk:
                    req.encoding = 'GBK'       #这里是网页的编码转换，根据网页的实际需要进行修改，经测试这个编码没有问题
                break
            except Exception as e:
                pass
                # time.sleep(random.choice(range(5, 10)))
        lock.acquire()
        self.html_buffer[url] = req.text
        lock.release()
        return req.text
    
    def get_html_img(self, url, is_buffer=False):
        if is_buffer:
            while not url in self.html_buffer.keys():
                time.sleep(0.1) 
        if url in self.html_buffer.keys():
            # print(url)
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
    
    def get_secret_map(self):
        with open('secret_map.cfg', 'rb') as f:
            self.secret_map = pickle.load(f)
        
    def make_folder(self):
        os.makedirs(self.temp_path, exist_ok=True)

        self.text_path = os.path.join(self.temp_path, 'OEBPS/Text')
        os.makedirs(self.text_path, exist_ok=True)

        self.img_path = os.path.join(self.temp_path,  'OEBPS/Images')
        os.makedirs(self.img_path, exist_ok=True)
    
    def get_index_url(self):
        cata_html = self.get_html(self.cata_page, is_gbk=False)
        cata_html = self.restore_chars(cata_html)
        bf = BeautifulSoup(cata_html, 'html.parser')
        chap_html_list = bf.find('ol', {'id': 'volumes'}).find_all('li')
        volume_array = 0
        name = ''
        img_url = ''
        chap_urls = []
        chap_names = []
        for chap_html in chap_html_list:
            if str(chap_html).startswith('<li class="chapter-bar chapter-li">'):
                volume_array += 1
                if volume_array==self.volume_no:
                    name = chap_html.text
            elif volume_array==self.volume_no:
                if str(chap_html).startswith('<li class="chapter-li jsChapter">'):
                    url = self.url_head + chap_html.find('a').get('href')
                    if chap_html.text == self.color_page_name:
                        img_url = url
                    else:
                        chap_names.append(chap_html.text)
                        chap_urls.append(url)
        self.volume = {'name': name, 'chap_names': chap_names, 'chap_urls':chap_urls, 'img_url': img_url}
    
    def get_chap_list(self):
        cata_html = self.get_html(self.cata_page, is_gbk=False)
        cata_html = self.restore_chars(cata_html)
        bf = BeautifulSoup(cata_html, 'html.parser')
        chap_html_list = bf.find('ol', {'id': 'volumes'}).find_all('li')
        volume_array = 0
        chap_names = []
        for chap_html in chap_html_list:
            if str(chap_html).startswith('<li class="chapter-bar chapter-li">'):
                volume_array += 1
                chap_names.append(chap_html.text)
        for chap_no, chap_name in enumerate(chap_names):
            print(f'[{chap_no+1}]', chap_name)

    def get_page_text(self, content_html):
        bf = BeautifulSoup(content_html, 'html.parser')
        text_with_head = bf.find('div', {'id': 'acontentz', 'class': 'bcontent'}) 
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
        text = self.restore_chars(text)
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
            content_html = self.get_html(url, is_buffer=True, is_gbk=False)
            text = self.get_page_text(content_html)
            text_chap += text
            url_new = url_ori.replace('.html', '_{}.html'.format(page_no+1))[len(self.url_head):]
            if url_new in content_html:
                page_no += 1
                url = self.url_head + url_new
            else:
                if return_next_chapter:
                    next_chap_url = self.url_head + re.search(r'nextpage="(.*?)"', content_html).group(1)
                break
        return text_chap, next_chap_url
    
    def get_text(self):
        img_strs = []
        self.make_folder()
        if self.is_color_page:
            is_fix_next_chap_url = (self.img_chap_name in self.missing_last_chap_list)
            text, next_chap_url = self.get_chap_text(self.volume['img_url'], self.img_chap_name, return_next_chapter=is_fix_next_chap_url)
            if is_fix_next_chap_url: 
                self.volume['chap_urls'][0] = next_chap_url #正向修复
            text_html_color = text2htmls(self.img_chap_name, text)
        
        if self.multi_thread:
            self.pre_request_img()
            
        for chap_no, (chap_name, chap_url) in enumerate(zip(self.volume['chap_names'], self.volume['chap_urls'])):
            is_fix_next_chap_url = (chap_name in self.missing_last_chap_list)
            text, next_chap_url = self.get_chap_text(chap_url, chap_name, return_next_chapter=is_fix_next_chap_url)
            if is_fix_next_chap_url: 
                self.volume['chap_urls'][chap_no+1] = next_chap_url #正向修复
            text_html = text2htmls(chap_name, text) 
            textfile = self.text_path + f'/{str(chap_no).zfill(2)}.xhtml'
            with open(textfile, 'w+', encoding='utf-8') as f:
                f.writelines(text_html)
            for text_line in text_html:
                img_str = re.search(r"<img(.*?)\/>", text_line)
                if img_str is not None:
                    img_strs.append(img_str.group(0))
            

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

    def get_html_buffer(self, url, is_img=False):
        if is_img:
            self.get_html_img(url)
        else:
            self.get_html(url)


    def write_page_dict(self, url, page_no):
        self.page_url_map[url] = page_no

    def get_page_num(self, url):
        req = self.get_html(url)
        mmm = r"<div class=\"atitle\"><h1 id=\"atitle\">(.*?)（2/(.*?)）"
        page_no = max(int(re.search(mmm, req).group(2)), 1)
        url = url.replace('_2.html', '.html')
        self.write_page_dict(url, page_no)

    def pre_request(self):
        page_urls = []
        for chap_url in self.volume['chap_urls']:
            if not self.check_url(chap_url):
                page_urls.append(chap_url.replace('.html', '_2.html'))
   
        page_pool = [self.pool.submit(self.get_page_num, url) for url in page_urls]
        wait(page_pool)

        for chap_url in self.volume['chap_urls']:
            if not self.check_url(chap_url):
                self.url_buffer.append(chap_url)
                for i in range(2, self.page_url_map[chap_url]+1):
                        self.url_buffer.append(chap_url.replace('.html', '_{}.html'.format(str(i))))

        # self.url_buffer = self.url_buffer[3:]
        if self.volume['img_url'] != '':
            self.url_buffer = [self.volume['img_url']] + self.url_buffer
        
   
        for i, url in enumerate(self.url_buffer):
            self.pool.submit(self.get_html_buffer, url, False)
        time.sleep(2)

    
    def pre_request_img(self):
        img_urls = list(self.img_url_map.keys())
        for i, url in enumerate(img_urls):
            self.pool.submit(self.get_html_buffer, url, True)

    def get_image(self, is_gui=False, signal=None):
        self.pre_request_img()
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

    def get_toc(self):
        toc_htmls = get_toc_html(self.title, self.volume["chap_names"])
        textfile = self.temp_path + '/OEBPS/toc.ncx'
        with open(textfile, 'w+', encoding='utf-8') as f:
            f.writelines(toc_htmls)

    def get_content(self):
        num_chap = len(self.volume["chap_names"])
        num_img = len(os.listdir(self.img_path))
        img_exist = (self.volume['img_url'] != '')
        content_htmls = get_content_html(self.title + '-' + self.volume['name'], self.author, num_chap, num_img, img_exist)
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
        epub_file = check_chars(self.epub_path + '/' + self.title + '-' + self.volume['name'] + '.epub')
        with zipfile.ZipFile(epub_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for dirpath, dirnames, filenames in os.walk(self.temp_path):
                fpath = dirpath.replace(self.temp_path,'') #这一句很重要，不replace的话，就从根目录开始复制
                fpath = fpath and fpath + os.sep or ''
                for filename in filenames:
                    zf.write(os.path.join(dirpath, filename), fpath+filename)
        shutil.rmtree(self.temp_path)
        return epub_file
    
    def check_volume(self, is_gui=False, signal=None, editline=None):
         #没有检测到插图页，手动输入插图页标题
        if self.volume['img_url'] == '':
            hand_in_name = self.hand_in_color_page_name(is_gui, signal, editline)
            if hand_in_name in self.volume['chap_names']:
                ind = self.volume['chap_names'].index(hand_in_name)
                self.volume['chap_names'].pop(ind)
                self.volume['img_url'] = self.volume['chap_urls'].pop(ind)

        #没有彩页 但主页封面存在，将主页封面设为书籍封面 
        if self.volume['img_url'] == '' and (not self.check_url(self.cover_url)):  
            self.is_color_page = False
            self.img_url_map[self.cover_url] = str(len(self.img_url_map)).zfill(2)
            print('**************')
            print('提示：没有彩页，但主页封面存在，将使用主页的封面图片作为本卷图书封面')
            print('**************')
        
        if self.check_url(self.volume['img_url']):
            if self.check_url(self.volume['chap_urls'][0]) and (not self.prev_fix_url(0, len(self.volume['chap_names']))): #如果第一章失效则使用反向递归修复程序, 反向再失败则手动输入
                self.volume['img_url'] = self.hand_in_url('插图', is_gui, signal, editline)
            else:
                self.volume['img_url'] = self.get_prev_url(0)

        chap_names = self.volume['chap_names']
        for chap_no, url in enumerate(self.volume['chap_urls']):
            if self.check_url(url):
                if not self.prev_fix_url(chap_no, len(self.volume['chap_names'])): #先尝试反向递归修复
                    if chap_no==0: #第一章反向修复失败，有插图页则使用正向修复，没有插图页则采用手动修复
                        if self.volume['img_url'] == '':
                            self.volume['chap_urls'][0] = self.hand_in_url(chap_names[chap_no], is_gui, signal, editline)
                        else:
                            self.missing_last_chap_list.append(self.img_chap_name)
                    else: #其他章节反向修复失败则采用正向修复
                        self.missing_last_chap_list.append(chap_names[chap_no-1])
        # print(self.missing_last_chap_list)
    
    def check_url(self, url):#当检测有问题返回True
        return ('javascript' in url or 'cid' in url)   
    
    def get_prev_url(self, chap_no): #获取前一个章节的链接
        content_html = self.get_html(self.volume['chap_urls'][chap_no], is_gbk=False)
        return self.url_head + re.search(r'prevpage="(.*?)"', content_html).group(1) 
    
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
    
    # 恢复函数，根据secret_map进行恢复
    def restore_chars(self, text):
        restored_text = ""
        i = 0
        while i < len(text):
            char = text[i]
            if char in self.secret_map:
                    restored_text += self.secret_map[char]
            else:
                    restored_text += char
            i += 1
        return restored_text
    
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