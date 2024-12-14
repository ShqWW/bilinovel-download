from .Downloader import Downloader
from .Editer import Editer
from .utils import *

def query_chaps(book_no):
    print('未输入卷号，将返回书籍目录信息......')
    downloader = Downloader(root_path='./out', book_no=book_no)
    print('--------------------------------')
    print(downloader.book_name, downloader.author)
    print('--------------------------------')
    downloader.get_chap_list()
    print('--------------------------------')
    print('请输入所需要的卷号进行下载。')

def download_single_volume(root_path,
                           book_no,
                           volume_no,
                           interval,
                           color_page,
                           is_gui=False,
                           hang_signal=None,
                           progressring_signal=None,
                           cover_signal=None,
                           edit_line_hang=None):
    
    downloader = Downloader(root_path=root_path, book_no=book_no, volume_no=volume_no, interval=interval, color_page=color_page)
    print('正在积极地获取书籍信息....')
    success = downloader.get_index_url()
    if not success:
        print('书籍信息获取失败')
        return
    print(downloader.book_name + '-' + downloader.volume['volume_name'], downloader.author)
    print('****************************')
    # if not editer.is_buffer():
    downloader.check_volume(is_gui=is_gui, signal=hang_signal, editline=edit_line_hang)
    print('正在下载漫画....')
    print('*********************') 
    downloader.get_manga(is_gui=is_gui, signal=progressring_signal)
    print('*********************')
    chap_list = downloader.volume['chap_names']
    editer = Editer(downloader.book_name, downloader.volume['volume_name'], downloader.volume_no, downloader.author, downloader.brief, downloader.tag_list,chap_list, downloader.comic_path, root_path, delete_comic=0)
    editer.get_cover(is_gui=is_gui, signal=cover_signal)
    editer.pack_img()
    editer.typesetting()
    editer.get_epub()

def downloader_router(root_path,
                      book_no,
                      volume_no,
                      interval=5000,
                      color_page=0,
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
            download_single_volume(root_path, book_no, volume_no, interval, color_page, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
        print('所有下载任务都已经完成！')
    else:
        download_single_volume(root_path, book_no, volume_no, interval, color_page, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
    

    
        

    

    
    
