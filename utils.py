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


def get_content_html(title, author, num_chap, num_img, img_exist=False):
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
    if img_exist:
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

def check_chars(win_chars):
    win_illegal_chars = '?*"<>|:/\\'
    new_chars = ''
    for char in win_chars:
        if char in win_illegal_chars:
            new_chars += '\u25A0'
        else:
            new_chars += char
    return new_chars
