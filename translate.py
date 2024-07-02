"""
This module provides functions to translate .epub from Simplified Chinese to Traditional Chinese.

Original source: stoneapptech/epub_convert/convert.py
Source URL: https://github.com/stoneapptech/epub_convert/blob/master/convert.py

Functions:
    translate_epub_with_path(epub_path): Translate the file at epub_path and make a new translated one in the same directory with different name.
"""

import zipfile
import opencc
from pathlib import Path

# only initailize OpenCC once, or it would be very slow
converter = opencc.OpenCC(config="s2tw.json")

def convert_epub(epub, output=None):
    target_filetype = ["htm", "html", "xhtml", "ncx", "opf"]

    origin = zipfile.ZipFile(epub, mode="r")
    copy = zipfile.ZipFile(output, mode="w")

    for i, fn in enumerate(origin.namelist()):
        info = origin.getinfo(fn)
        extension = Path(fn).suffix[1:] # remove heading `.`
        if extension in target_filetype:
            # if file extension is targeted file type
            sc_content = origin.read(fn)
            tc_content = convert_content(sc_content)
            if extension == "opf":
                tc_content = tc_content.replace("<dc:language>zh-CN</dc:language>", "<dc:language>zh-TW</dc:language>")
            copy.writestr(s2t(fn), tc_content, compress_type=info.compress_type)
        else:
            # write other files directly
            copy.writestr(s2t(fn), origin.read(fn), compress_type=info.compress_type)

    origin.close()
    copy.close()
    return output

def convert_content(content):
    _tmp = []

    for line in content.splitlines():
        _tmp.append(s2t(line))

    return "\n".join(_tmp)

def s2t(text):
    return converter.convert(text)

def translate_epub_with_path(epub_path):
    import time
    from io import BytesIO
    path = Path(epub_path)
    directory = path.parent.absolute()
    filename = path.name

    if not path.suffix == ".epub":
        print(f"跳過 {epub_path} 因為此非 .epub 檔案")
        return 0, None
    elif filename == s2t(filename):
        output_fn = epub_path[:-5] + '-tc.epub'
    else:
        output_fn = s2t(filename)

    t = time.time()
    print(f"正在翻譯成繁體 {epub_path}")
    buffer = BytesIO()
    output = convert_epub(epub_path, buffer)
    with open(Path.joinpath(directory, output_fn), "wb") as f:
        f.write(buffer.getvalue())
    print(f"翻譯成功！ {output_fn}")
    print(f"翻譯耗時: {round(time.time() - t, 2)}s")
    return 1, output_fn