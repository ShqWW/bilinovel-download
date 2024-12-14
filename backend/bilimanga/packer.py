from .Editer import Editer
import os

if __name__=='__main__':
    title = '魔法少女小圓☆魔獸篇'
    bookname = '第三卷'
    author = 'ハノカゲ'
    brief = '魔法少女小圓☆魔獸篇漫畫 ，《魔法少女小圓 [魔獸篇]》是2011年播出的日本原創動畫《魔法少女小圓》的衍生漫畫之一，由本篇漫畫《魔法少女小圓》的作者ハノカゲ作畫，於芳文社旗下的《Manga Time Kirara Magica》2015年7月號開始連載。'
    tag_list = ['百合', '奇幻']
    chap_list = ['彩页','第7话','第8话','第9话']
    root = 'C:/Users/haoru/Desktop'
    comic_root = os.path.join(root, title+'-'+bookname)
    out_root= root
    editer = Editer(book_name=title, author=author, brief=brief, tag_list=tag_list, chap_list=chap_list, comic_root=comic_root, out_root=out_root, volume_name=bookname)
    editer.pack_img()
    editer.typesetting()
    editer.get_epub()