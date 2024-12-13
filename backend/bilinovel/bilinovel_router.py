
from .Editer import Editer
from backend.bilinovel.utils import *



def query_chaps(book_no):
    print('未输入卷号，将返回书籍目录信息......')
    editer = Editer(root_path='./out', book_no=book_no)
    print('--------------------------------')
    print(editer.title, editer.author)
    print('--------------------------------')
    editer.get_chap_list()
    print('--------------------------------')
    print('请输入所需要的卷号进行下载。')

def download_single_volume(root_path,
                           book_no,
                           volume_no,
                           interval,
                           num_thread,
                           is_gui=False,
                           hang_signal=None,
                           progressring_signal=None,
                           cover_signal=None,
                           edit_line_hang=None):
    
    editer = Editer(root_path=root_path, book_no=book_no, volume_no=volume_no, interval=interval, num_thread=num_thread)
    print('正在积极地获取书籍信息....')
    success = editer.get_index_url()
    if not success:
        print('书籍信息获取失败')
        return
    print(editer.title + '-' + editer.volume['book_name'], editer.author)
    print('****************************')
    # if not editer.is_buffer():
    editer.check_volume(is_gui=is_gui, signal=hang_signal, editline=edit_line_hang)
    print('正在下载文本....')
    print('*********************') 
    editer.get_text()
    print('*********************')
    # editer.buffer()
    # else:
    #     print('检测到文本文件，直接下载插图')
    #     editer.buffer()
    

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
                      interval=500,
                      num_thread=1,
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
            download_single_volume(root_path, book_no, volume_no, interval, num_thread, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
        print('所有下载任务都已经完成！')
    else:
        download_single_volume(root_path, book_no, volume_no, interval, num_thread, is_gui, hang_signal, progressring_signal, cover_signal, edit_line_hang)
    

    
        

    

    
    
