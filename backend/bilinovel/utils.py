from backend.rubbish_secret_map import rubbish_secret_map, blank_list
from bs4 import BeautifulSoup

def get_container_html():
    text_html = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>"""
    return text_html

def get_cover_html(img_w, img_h):
    text_html = f"""<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Cover</title>
</head>
<body>
  <div style="text-align: center; padding: 0pt; margin: 0pt;">
    <svg xmlns="http://www.w3.org/2000/svg" height="100%" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="0 0 {img_w} {img_h}" width="100%" xmlns:xlink="http://www.w3.org/1999/xlink">
      <image width="{img_w}" height="{img_h}" xlink:href="../Images/00.jpg"/>
    </svg>
  </div>
</body>
</html>"""
    return text_html

def text2htmls(chap_name, text):
    text_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<!--?xml version="1.0" encoding="UTF-8" standalone="no"?--><html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{chap_name}</title>
    <style>p {{ text-indent: 2em; }}</style>
</head>
<body>
<h1>{chap_name}</h1>
{text}
</body>
</html>"""
    return text_html

def get_toc_html(title, chap_names):
    toc_html_template = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
   "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:a18aac05-497d-476d-b66f-0211f609743d" />
    <meta name="dtb:depth" content="0" />
    <meta name="dtb:totalPageCount" content="0" />
    <meta name="dtb:maxPageNumber" content="0" />
  </head>
  <docTitle>
    <text>{title}</text>
  </docTitle>
  <navMap>
{nav_points}
  </navMap>
</ncx>"""
    nav_point_template = """    <navPoint id="navPoint-{nav_id}" playOrder="{play_order}">
    <navLabel>
        <text>{chap_name}</text>
    </navLabel>
    <content src="Text/{chap_no}.xhtml"/>
    </navPoint>"""
    nav_points = '\n'.join(
        nav_point_template.format(nav_id=i+1, play_order=i+1, chap_name=chap_name, chap_no=str(i).zfill(2))
        for i, chap_name in enumerate(chap_names)
    )
    return toc_html_template.format(title=title, nav_points=nav_points)



def get_content_html(book_name, volume_name, volume_no, author, publisher, brief, tag_list, num_chap, num_img, img_exist=False):
    content_html_template = """<?xml version="1.0" encoding="utf-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:language>zh-CN</dc:language>
    <meta name="calibre:series" content="{series_name}" />
    <meta name="calibre:series_index" content="{series_no}"/>
    <dc:title>{title}</dc:title>
    <dc:creator>{author}</dc:creator>
    <dc:publisher>{publisher}</dc:publisher>
    <dc:description>{brief}</dc:description>
{subjects}
    <meta name="cover" content="x00.jpg"/>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="cover.xhtml" href="Text/cover.xhtml" media-type="application/xhtml+xml"/>
{xcolor}
{chapters}
{images}
  </manifest>
  <spine toc="ncx">
    <itemref idref="cover.xhtml"/>
{spine_xcolor}
{spine_chapters}
  </spine>
  <guide>
    <reference type="cover" title="封面" href="Text/cover.xhtml"/>
  </guide>
</package>"""

    subjects = '\n'.join(f'    <dc:subject>{tag}</dc:subject>' for tag in tag_list)
    chapters = '\n'.join(
        f'    <item id="x{str(chap_no).zfill(2)}.xhtml" href="Text/{str(chap_no).zfill(2)}.xhtml" media-type="application/xhtml+xml"/>'
        for chap_no in range(num_chap)
    )
    images = '\n'.join(
        f'    <item id="x{str(img_no).zfill(2)}.jpg" href="Images/{str(img_no).zfill(2)}.jpg" media-type="image/jpeg"/>'
        for img_no in range(num_img)
    )
    spine_chapters = '\n'.join(
        f'    <itemref idref="x{str(chap_no).zfill(2)}.xhtml"/>'
        for chap_no in range(num_chap)
    )

    xcolor = '    <item id="xcolor" href="Text/color.xhtml" media-type="application/xhtml+xml"/>\n' if img_exist else ''
    spine_xcolor = '    <itemref idref="xcolor"/>\n' if img_exist else ''

    return content_html_template.format(
        series_name=book_name,
        series_no = volume_no,
        title=book_name+'-'+volume_name,
        author=author,
        publisher=publisher,
        brief = brief,
        subjects=subjects,
        chapters=chapters,
        images=images,
        xcolor=xcolor,
        spine_xcolor=spine_xcolor,
        spine_chapters=spine_chapters
    )

def check_chars(win_chars):
    win_illegal_chars = '?*"<>|:/'
    new_chars = ''
    for char in win_chars:
        if char in win_illegal_chars:
            new_chars += '\u25A0'
        else:
            new_chars += char
    return new_chars

# def replace_rubbish_text(content_html):
#     soup = BeautifulSoup(content_html, 'html.parser')
#     ps = soup.find_all('p')
#     if not ps:
#         return str(soup)
#     last_p = ps[-1]
#     text = last_p.get_text()
#     sb = []
#     for blank_char in text:
#         # if blank_char in blank_list:
#         #     continue
#         replacement = rubbish_secret_map.get(blank_char)
#         t = replacement if replacement else blank_char
#         sb.append(t)
#     last_p.string = ''.join(sb)
#     return str(soup)

chinese_punctuation = "，。！？、；：“”‘’（）《》〈〉【】『』〖〗…—～＋－＝×÷·—‘’“”『』【】（）《》〈〉「」『』〖〗〘〙〚〛〚〛〘〙〖〗〘〙〚〛〘〙〖〗〘〙"

def replace_rubbish_text(content_html):
    soup = BeautifulSoup(content_html, 'html.parser')
    ps = soup.find_all('p')
    if not ps:
        return str(soup)
    last_p = ps[-1]
    text = last_p.get_text()
    sb = []
    for blank_char in text:
        replace_strr = rubbish_secret_map.get(blank_char)
        if replace_strr is not None:
            sb.append(replace_strr)
            print(replace_strr)
        elif blank_char in chinese_punctuation:
            sb.append(blank_char)
    last_p.string = ''.join(sb)
    return str(soup)