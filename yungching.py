from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from time import time ,sleep
import json
import random
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from requests_html import HTMLSession

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
    # 拿到現在的ip
    proxy = j_ip_txt['ip']
    # 使用http跟https的方法
    proxies = {"http": proxy, "https": proxy}
    return proxies

def get_Data(url,n):
    t = random.randint(1,10)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    # cookie = driver.get_cookies()
    driver.quit()
    # proxy = proxies()
    user_agent=UserAgent()
    file_path = 'C:/Users/88698/Desktop/example.xlsx'
    header = {'User-Agent': user_agent.random}
    proxy = proxies()
    default_response = requests.get(url, headers=header,proxies=proxy)
    cookies_key1 = 'SEID_G'
    cookies_key2 = 'TRID_G'
    cookies_key3 = 'yawbewkcehc'
    print(default_response.cookies)
    cookies1 = {
                cookies_key1:default_response.cookies[cookies_key1],
                cookies_key2:default_response.cookies[cookies_key2],
                cookies_key3:default_response.cookies[cookies_key3]
                }
    response = requests.get(url,cookies=cookies1, headers=header)
    url_list = []
    
    soup = BeautifulSoup(response.text, "lxml")
    urls = soup.find_all('a', class_="item-title ga_click_trace")
    for u in urls:
        url_list.append(f"https://buy.yungching.com.tw{u['href']}")
    data_list = []
    for link in url_list:
        # res = requests.get(link, headers=header)
        default_response = requests.get(link, headers=header)
        cookies_key1 = 'SEID_G'
        cookies_key2 = 'TRID_G'
        cookies_key3 = 'yawbewkcehc'
        cookies1 = {
                    cookies_key1: default_response.cookies[cookies_key1],
                    cookies_key2: default_response.cookies[cookies_key2],
                    cookies_key3:default_response.cookies[cookies_key3]
                    }
        session = HTMLSession()
        response = session.get(link,cookies=cookies1,headers=header,proxies=proxy)
        response.html.render(timeout=50000)
        res = requests.get(link, cookies=cookies1, headers=header,proxies=proxy)
        link_soup = BeautifulSoup(res.text, 'lxml')
        title = link_soup.find("h1", class_="house-info-name").get_text().split('\n', 1)[0]
        low_price = link_soup.find("em").get_text()
        name = response.html.find('app-case-contact-info div.manager-name',first=True).text
        buliding = link_soup.select_one(
            "body > main > section.m-house-infomation.true-value > div.m-house-infos.right > div.m-house-info-wrap > div:nth-child(1) > div > span").get_text()
        room = link_soup.select_one(
            "body > main > section.m-house-infomation.true-value > div.m-house-infos.right > div.m-house-info-wrap > div:nth-child(2) > div").get_text().split('\n', 1)[1]
        year = link_soup.select_one(
            "body > main > section.m-house-infomation.true-value > div.m-house-infos.right > div.m-house-info-wrap > div:nth-child(3) > div").get_text().replace('\n','')
        address = link_soup.find('div', class_="house-info-addr").get_text()
        house_num = link_soup.find('div', class_="house-info-num").get_text()
        use = link_soup.select_one(
            "body > main > section.m-house-detail-block.detail-data > section.m-house-detail-list.bg-square > ul > li:nth-child(4)").get_text()
        if room == []:
            data = dict()
            data["subject"]=str(title)
            data["price"]=str(low_price)
            data["building_ping"]=buliding
            data["house_age"]=year
            data["address"]=address
            data["house_type"]=use
            data["contect_man"]=name
            data_list.append(data)
            print(title, low_price, buliding, year, address,use,name)
        else:
            data = dict()
            data["subject"]=str(title)
            data["price"]=str(low_price)
            data["building_ping"]=buliding
            data["house_age"]=year
            data["address"]=address
            data["house_type"]=use
            data["contect_man"]=name
            data_list.append(data)
            print(title, low_price, buliding, year, address, house_num, use, room,name)
    df = pd.DataFrame(data_list)
    
    # with pd.ExcelWriter(file_path, mode='a') as writer:
    #     df.to_excel(writer, sheet_name=f"Sheet{n}", index=False)
    next_link = soup.select_one("body > main > div.l-main-list > div.m-pagination > ul > li:nth-child(13) > a")
    if next_link is None:
        return '無更多資料'
    else:
        next_url = "https://buy.yungching.com.tw" + next_link['href']
        print("下一頁URL：", next_url)
        n+=1
        sleep(t)
        get_Data(next_url,n)


url = 'https://buy.yungching.com.tw/'
get_Data(url,0)