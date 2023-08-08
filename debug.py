import requests
import time 
import random
from utils import *
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import re
import urllib
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47', 'referer': "https://w.linovelib.com/"}

img_url = 'https://img3.readpai.com/0/75/145573/172818.jpg'
# img_url = "http://pic.wenku8.com/pictures/2/2692/145153/178471.jpg"
# img_url = "https://img3.readpai.com/3/3728/194160/216776.jpg"
r=requests.get(img_url, headers=header)
with open('./a.jpg', 'wb') as f:
    f.write(r.content) #写入二进制内容


# urllib.request.urlretrieve(img_url, './a.jpg')




