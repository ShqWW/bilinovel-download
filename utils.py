def get_cover_html(img_w, img_h):
    img_htmls = []
    img_msg = '      <image width=\"'+ str(img_w)+'\" height=\"'+ str(img_h)+'\" xlink:href="../Images/00.jpg"/>\n'
    img_htmls.append('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
    img_htmls.append('<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\"\n')
    img_htmls.append('\"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n')
    img_htmls.append('<html xmlns=\"http://www.w3.org/1999/xhtml\">\n')
    img_htmls.append('<head>\n')
    img_htmls.append('  <title>Cover</title>\n')
    img_htmls.append('</head>\n')
    img_htmls.append('<body>\n')
    img_htmls.append('  <div style="text-align: center; padding: 0pt; margin: 0pt;">\n')
    img_htmls.append('    <svg xmlns=\"http://www.w3.org/2000/svg\" height=\"100%\" preserveAspectRatio=\"xMidYMid meet\" version=\"1.1\" viewBox=\"0 0 '+ str(img_w)+' '+ str(img_h)+'\" width=\"100%\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n')
    img_htmls.append(img_msg)
    img_htmls.append('    </svg>\n')
    img_htmls.append('  </div>\n')
    img_htmls.append('</body>\n')
    img_htmls.append('</html>')
    return img_htmls


def text2htmls(chap_name, text):
    text_lines = text.split('\n')
    text_body = []
    text_body.append('<body>\n')
    text_body.append('<h1>' + chap_name + '</h1>\n')
    for text_line in text_lines:
        if text_line.startswith('[img:'):
            img_no = text_line[5:7]
            text_line_html = f'  <img alt=\"{img_no}\" src=\"../Images/{img_no}.jpg\"/>\n'
        else:
            text_line_html = '<p>' + text_line + '</p>\n'
        text_body.append(text_line_html)
    text_body.append('</body>\n')
    text_head = []
    text_head.append('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n')
    text_head.append('<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\"\n')
    text_head.append('\"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">\n')
    text_head.append('<html xmlns=\"http://www.w3.org/1999/xhtml\">\n')
    text_head.append('<head>\n')
    text_head.append('<title>'+ chap_name+'</title>\n')
    text_head.append('<style>p{text-indent:2em;}</style>\n')
    text_head.append('</head>\n')
    text_htmls = text_head + text_body + ['</html>']
    return text_htmls

def get_toc_html(title, chap_names):
    toc_htmls = []
    toc_htmls.append('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n')
    toc_htmls.append('<!DOCTYPE ncx PUBLIC \"-//NISO//DTD ncx 2005-1//EN\"\n')
    toc_htmls.append('   \"http://www.daisy.org/z3986/2005/ncx-2005-1.dtd\">\n\n')
    toc_htmls.append('<ncx xmlns=\"http://www.daisy.org/z3986/2005/ncx/\" version=\"2005-1\">\n')
    toc_htmls.append('  <head>\n')
    toc_htmls.append('    <meta name=\"dtb:uid\" content=\"urn:uuid:a18aac05-497d-476d-b66f-0211f609743d\" />\n')
    toc_htmls.append('    <meta name=\"dtb:depth\" content=\"0\" />\n')
    toc_htmls.append('    <meta name=\"dtb:totalPageCount\" content=\"0\" />\n')
    toc_htmls.append('    <meta name=\"dtb:maxPageNumber\" content=\"0\" />\n')
    toc_htmls.append('  </head>\n')
    toc_htmls.append('<docTitle>\n')
    toc_htmls.append('  <text>'+ title +'</text>\n')
    toc_htmls.append('</docTitle>\n')
    toc_htmls.append('<navMap>\n')
    for chap_no, chap_name in enumerate(chap_names):
        toc_htmls.append('    <navPoint id=\"navPoint-'+str(chap_no+1)+'\" playOrder=\"'+str(chap_no+1)+'\">\n')
        toc_htmls.append('      <navLabel>\n')
        toc_htmls.append('        <text>'+ chap_name +'</text>\n')
        toc_htmls.append('      </navLabel>\n')
        toc_htmls.append('      <content src="Text/'+str(chap_no).zfill(2)+'.xhtml"/>\n')
        toc_htmls.append('    </navPoint>\n')
    toc_htmls.append('</navMap>\n')
    toc_htmls.append('</ncx>')
    return toc_htmls


def get_content_html(title, author, num_chap, num_img, volume):
    content_htmls = []
    content_htmls.append('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n')
    content_htmls.append('<package version=\"2.0\" unique-identifier=\"BookId\" xmlns=\"http://www.idpf.org/2007/opf\">\n')
    content_htmls.append('  <metadata xmlns:dc=\"http://purl.org/dc/elements/1.1/\" xmlns:opf=\"http://www.idpf.org/2007/opf\">\n')
    content_htmls.append('    <dc:identifier id=\"BookId\" opf:scheme=\"UUID\">urn:uuid:942b8224-476b-463b-9078-cdfab0ee2686</dc:identifier>\n')
    content_htmls.append('    <dc:language>zh</dc:language>\n')
    content_htmls.append('    <dc:title>'+ title +'</dc:title>\n')
    content_htmls.append('    <dc:creator opf:role="aut" opf:file-as="未知">'+ author +'</dc:creator>\n')
    content_htmls.append('    <meta name=\"cover\" content=\"x00.jpg\"/>\n')
    content_htmls.append('  </metadata>\n')
    content_htmls.append('  <manifest>\n')
    content_htmls.append('    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n')
    content_htmls.append('    <item id="cover.xhtml" href="Text/cover.xhtml" media-type="application/xhtml+xml"/>\n')
    if volume['img_url'] != '':
        content_htmls.append('    <item id="xcolor" href="Text/color.xhtml" media-type="application/xhtml+xml"/>\n')
    for chap_no in range(num_chap):
        content_htmls.append('    <item id=\"x'+str(chap_no).zfill(2)+'.xhtml\" href=\"Text/'+ str(chap_no).zfill(2)+'.xhtml\" media-type=\"application/xhtml+xml\"/>\n')


    for img_no in range(num_img):
        content_htmls.append('    <item id=\"x'+str(img_no).zfill(2)+'.jpg\" href=\"Images/'+ str(img_no).zfill(2)+'.jpg\" media-type=\"image/jpeg\"/>\n')

    content_htmls.append('  </manifest>\n')
    content_htmls.append('  <spine toc="ncx">\n')


    content_htmls.append('    <itemref idref="cover.xhtml"/>\n')
    content_htmls.append('    <itemref idref="xcolor"/>\n')
    for chap_no in range(num_chap):
        content_htmls.append('    <itemref idref=\"x'+str(chap_no).zfill(2)+'.xhtml\"/>\n')

    content_htmls.append('  </spine>\n')
    content_htmls.append('  <guide>\n')
    content_htmls.append('    <reference type="cover" title="封面" href="Text/cover.xhtml"/>\n')
    content_htmls.append('  </guide>\n')
    content_htmls.append('</package>\n')
    return content_htmls


def get_container_html():
    container_htmls = []
    container_htmls.append('<?xml version="1.0" encoding="UTF-8"?>\n')
    container_htmls.append('<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n')
    container_htmls.append('    <rootfiles>\n')
    container_htmls.append('        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n')
    container_htmls.append('   </rootfiles>\n')
    container_htmls.append('</container>\n')
    return container_htmls


def get_color_html(colorimg_num):
    color_htmls = []
    color_htmls.append('<?xml version=\"1.0\" encoding=\"utf-8\"?>\n')
    color_htmls.append('<html>\n')
    color_htmls.append('<head>\n')

    color_htmls.append('  <title>彩插</title>\n')
    color_htmls.append('</head>\n')
    color_htmls.append('<body>\n')
    for i in range(1, colorimg_num):
        color_htmls.append('  <img alt=\"'+str(i).zfill(2)+'\" src=\"../Images/'+str(i).zfill(2)+'.jpg\"/>\n')
    color_htmls.append('</body>\n')
    color_htmls.append('</html>')
    return color_htmls


def get_vol(vol_no):
    vol_no = str(vol_no)
    s="零一二三四五六七八九"
    for c in "0123456789":
        vol_no=vol_no.replace(c,s[eval(c)])
    vol_no = '第' + vol_no + '卷'
    return vol_no

secretMap = {
        "\u201C": "「",
        "\u201D": "」",
        "\u2018": "『",
        "\u2019": "』",
        "\uE82C": "的",
        "\uE852": "一",
        "\uE82D": "是",
        "\uE819": "了",
        "\uE856": "我",
        "\uE857": "不",
        "\uE816": "人",
        "\uE83C": "在",
        "\uE830": "他",
        "\uE82E": "有",
        "\uE836": "这",
        "\uE859": "个",
        "\uE80A": "上",
        "\uE855": "们",
        "\uE842": "来",
        "\uE858": "到",
        "\uE80B": "时",
        "\uE81F": "大",
        "\uE84A": "地",
        "\uE853": "为",
        "\uE81E": "子",
        "\uE822": "中",
        "\uE813": "你",
        "\uE85B": "说",
        "\uE807": "生",
        "\uE818": "国",
        "\uE810": "年",
        "\uE812": "着",
        "\uE851": "就",
        "\uE801": "那",
        "\uE80C": "和",
        "\uE815": "要",
        "\uE84C": "她",
        "\uE840": "出",
        "\uE848": "也",
        "\uE835": "得",
        "\uE800": "里",
        "\uE826": "后",
        "\uE863": "自",
        "\uE861": "以",
        "\uE854": "会",
        "\uE827": "家",
        "\uE83B": "可",
        "\uE85D": "下",
        "\uE84D": "而",
        "\uE862": "过",
        "\uE81C": "天",
        "\uE81D": "去",
        "\uE860": "能",
        "\uE843": "对",
        "\uE82F": "小",
        "\uE802": "多",
        "\uE831": "然",
        "\uE84B": "于",
        "\uE837": "心",
        "\uE829": "学",
        "\uE85E": "么",
        "\uE83A": "之",
        "\uE832": "都",
        "\uE808": "好",
        "\uE841": "看",
        "\uE821": "起",
        "\uE845": "发",
        "\uE803": "当",
        "\uE828": "没",
        "\uE81B": "成",
        "\uE83E": "只",
        "\uE820": "如",
        "\uE84E": "事",
        "\uE85A": "把",
        "\uE806": "还",
        "\uE83F": "用",
        "\uE833": "第",
        "\uE811": "样",
        "\uE804": "道",
        "\uE814": "想",
        "\uE80F": "作",
        "\uE84F": "种",
        "\uE80E": "开",
        "\uE823": "美",
        "\uE849": "乳",
        "\uE805": "阴",
        "\uE809": "液",
        "\uE81A": "茎",
        "\uE844": "欲",
        "\uE847": "呻",
        "\uE850": "肉",
        "\uE824": "交",
        "\uE85F": "性",
        "\uE817": "胸",
        "\uE85C": "私",
        "\uE838": "穴",
        "\uE82A": "淫",
        "\uE83D": "臀",
        "\uE82B": "舔",
        "\uE80D": "射",
        "\uE839": "脱",
        "\uE834": "裸",
        "\uE846": "骚",
        "\uE825": "唇"
}

# 恢复函数，根据secretMap进行恢复
def restore_chars(text):
        restored_text = ""
        i = 0
        while i < len(text):
                char = text[i]
                if char in secretMap:
                        restored_text += secretMap[char]
                else:
                        restored_text += char
                i += 1
        return restored_text