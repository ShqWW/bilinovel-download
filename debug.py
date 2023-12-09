# import threading

# def get222(url):
#     print(url)
#     # req = get_html(url)
#     # print(req)


# def get_multi_html(urls):
#     for i in range(4):
#         # print(urls[i])
#         a = threading.Thread(target=get222, args=(urls[i],))
#         a.start()

# urls = ['https://www.bilinovel.com/novel/3800/200529.html',
# 'https://www.bilinovel.com/novel/3800/200530.html',
# 'https://www.bilinovel.com/novel/3800/200531.html',
# 'https://www.bilinovel.com/novel/3800/200532.html']

# print(urls)

# get_multi_html(urls)

from selenium import webdriver
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge

edge_options = EdgeOptions()
edge_options.use_chromium = True
# 设置无界面模式，也可以添加其它设置
edge_options.add_argument('headless')
driver = Edge(options=edge_options)
r = driver.get('https://www.bilinovel.com/novel/3800/200529.html')
print(driver.page_source)
driver.quit()
