from requests_html import HTMLSession
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
import os,re,time,json
import random
from fake_useragent import UserAgent


url = 'http://nsp.tcd.gov.tw/ngis/'

def proxies():
    url = "https://bard.yeshome.net.tw/proxy/proxy_ip_v3/"
    data = {
        'twip': True,
        'tag_data': 'usezone'
    }
    res = requests.post(url, data=data)
    # '{"ip": "118.160.135.176:21210", "status": {"twip": "True", "tag_data": "use_XXX"}}'
    ip_txt = res.text
    j_ip_txt = json.loads(ip_txt)
    while True:
        try:
            # 拿到現在的ip
            proxy = j_ip_txt['ip']
            break
        except:
            print("抓不到ip,重新抓取中...")
            res = requests.post(url, data=data)
            # '{"ip": "118.160.135.176:21210", "status": {"twip": "True", "tag_data": "use_XXX"}}'
            ip_txt = res.text
            j_ip_txt = json.loads(ip_txt)
    # 使用http跟https的方法
    proxies = {"http": proxy, "https": proxy}
    return proxies


user_agent=UserAgent()
header = {'User-Agent': user_agent.random }
proxy = proxies()
print('工作中')
response = requests.get(url,headers=header,proxies=proxy)
soup = BeautifulSoup(response.text,'html.parser')
test=soup.select('script')
print('請稍等')
print(test)