import argparse
from Editer import Editer
import os
import shutil
from utils import *

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='config')
    parser.add_argument('--book_no', default='0000', type=str)
    parser.add_argument('--volume_no', default='1', type=int)
    parser.add_argument('--no_input', default=False, type=bool)
    args = parser.parse_args()
    return args


def query_chaps(book_no):
    print('未输入卷号，将返回书籍目录信息......')
    editer = Editer(root_path='./out', book_no=book_no)
    print('*******************************')
    print(editer.title, editer.author)
    print('*******************************')
    editer.get_chap_list()
    print('*******************************')
    print('请输入所需要的卷号进行下载（多卷可以用英文逗号分隔或直接使用连字符，详情见说明）')

temp_path = ''

def delete_tmp():
    print(temp_path)
    if os.path.exists(temp_path): 
        shutil.rmtree(temp_path)

def download_single_volume(root_path,
                           book_no,
                           volume_no,
                           is_gui=False,
                           hang_signal=None,
                           progressring_signal=None,
                           cover_signal=None,
                           edit_line_hang=None):
    
    editer = Editer(root_path=root_path, book_no=book_no, volume_no=volume_no)
    print('正在积极地获取书籍信息....')
    success = editer.get_index_url()
    if not success:
        print('书籍信息获取失败')
        return
    print(editer.title + '-' + editer.volume['book_name'], editer.author)
    print('****************************')
    temp_path = editer.temp_path
    if not editer.is_buffer():
        editer.check_volume(is_gui=is_gui, signal=hang_signal, editline=edit_line_hang)
        print('正在下载文本....')
        print('*********************') 
        editer.get_text()
        print('*********************')
        editer.buffer()
    else:
        print('检测到文本文件，直接下载插图')
        editer.buffer()
    

    print('正在下载插图.....................................')
    editer.get_image(is_gui=is_gui, signal=progressring_signal)
    
    print('正在编辑元数据....')
    editer.get_cover(is_gui=is_gui, signal=cover_signal)
    editer.get_toc()
    editer.get_content()
    editer.get_epub_head()

    print('正在生成电子书....')
    epub_file = editer.get_epub()
    print('生成成功！', f'电子书路径【{epub_file}】')
    

def downloader_router(root_path,
                      book_no,
                      volume_no,
                      is_gui=False, 
                      hang_signal=None,
                      progressring_signal=None,
                      cover_signal=None,
                      edit_line_hang=None):
    is_multi_chap = False
    if len(book_no)==0:
        print('请检查输入是否完整正确！')
        return
    elif volume_no == '':
        query_chaps(book_no)
        return 
    elif volume_no.isdigit():
        volume_no = int(volume_no)
        if volume_no<=0:
            print('请检查输入是否完整正确！') 
            return
    elif "-" in volume_no:
        start, end = map(str, volume_no.split("-"))
        if start.isdigit() and end.isdigit() and int(start)>0 and int(start)<int(end):
            volume_no_list = list(range(int(start), int(end) + 1))
            is_multi_chap = True
        else:
            print('请检查输入是否完整正确！')
            return
    elif "," in volume_no:
        volume_no_list = [num for num in volume_no.split(",")]
        if all([num.isdigit() for num in volume_no_list]):
            volume_no_list = [int(num) for num in volume_no_list] 
            is_multi_chap = True
        else:
            print('请检查输入是否完整正确！')
            return
    else:
            print('请检查输入是否完整正确！')
            return
    if is_multi_chap:
        for volume_no in volume_no_list:
            download_single_volume(root_path, book_no, volume_no, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
        print('所有下载任务都已经完成！')
    else:
        download_single_volume(root_path, book_no, volume_no, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
    
if __name__=='__main__':
    args = parse_args()
    download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

    if args.no_input:
        downloader_router(root_path='out', book_no=args.book_no, volume_no=args.volume_no)
    else:
        while True:
            args.book_no = input('请输入书籍号：')
            args.volume_no = input('请输入卷号(查看目录信息不输入直接按回车，下载多卷请使用逗号分隔或者连字符-)：')
            downloader_router(root_path='out', book_no=args.book_no, volume_no=args.volume_no)
            # args.book_no = '3800'
            # args.volume_no = '1'
            # downloader_router(root_path='out', book_no=args.book_no, volume_no=args.volume_no)
            # exit(0)
    
        

    

    
    
