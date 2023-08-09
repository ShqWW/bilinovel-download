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
        "\uE80C": "的",
        "\uE80D": "一",
        "\uE80E": "是",
        "\uE806": "了",
        "\uE807": "我",
        "\uE808": "不",
        "\uE80F": "人",
        "\uE810": "在",
        "\uE811": "他",
        "\uE812": "有",
        "\uE809": "这",
        "\uE80A": "个",
        "\uE80B": "上",
        "\uE813": "们",
        "\uE814": "来",
        "\uE815": "到",
        "\uE802": "时",
        "\uE803": "大",
        "\uE804": "地",
        "\uE805": "为",
        "\uE817": "子",
        "\uE818": "中",
        "\uE819": "你",
        "\uE81D": "说",
        "\uE81E": "生",
        "\uE816": "国",
        "\uE800": "年",
        "\uE801": "着",
        "\uE81A": "就",
        "\uE81B": "那",
        "\uE81C": "和",
        "\uE81F": "要",
        "\uE820": "她",
        "\uE821": "出",
        "\uE822": "也",
        "\uE823": "得",
        "\uE824": "里",
        "\uE825": "后",
        "\uE826": "自",
        "\uE827": "以",
        "\uE828": "会",
        "\uE82D": "家",
        "\uE82E": "可",
        "\uE831": "下",
        "\uE832": "而",
        "\uE833": "过",
        "\uE834": "天",
        "\uE82F": "去",
        "\uE830": "能",
        "\uE829": "对",
        "\uE82A": "小",
        "\uE82B": "多",
        "\uE82C": "然",
        "\uE837": "于",
        "\uE838": "心",
        "\uE839": "学",
        "\uE835": "么",
        "\uE846": "之",
        "\uE847": "都",
        "\uE83A": "好",
        "\uE83B": "看",
        "\uE836": "起",
        "\uE84A": "发",
        "\uE84B": "当",
        "\uE84C": "没",
        "\uE84D": "成",
        "\uE83C": "只",
        "\uE83D": "如",
        "\uE83E": "事",
        "\uE841": "把",
        "\uE842": "还",
        "\uE843": "用",
        "\uE844": "第",
        "\uE845": "样",
        "\uE83F": "道",
        "\uE840": "想",
        "\uE858": "作",
        "\uE859": "种",
        "\uE85A": "开",
        "\uE84F": "美",
        "\uE848": "乳",
        "\uE849": "阴",
        "\uE84E": "液",
        "\uE855": "茎",
        "\uE856": "欲",
        "\uE857": "呻",
        "\uE850": "肉",
        "\uE851": "交",
        "\uE852": "性",
        "\uE853": "胸",
        "\uE854": "私",
        "\uE85D": "穴",
        "\uE85E": "淫",
        "\uE85F": "臀",
        "\uE860": "舔",
        "\uE85B": "射",
        "\uE85C": "脱",
        "\uE861": "裸",
        "\uE862": "骚",
        "\uE863": "唇"
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