from time import sleep
from threading import Thread, Lock
from random import randint
from threading import Thread
import json
import time
import re
import tkinter
import tkinter.messagebox
from threading import Thread
import requests as req
from requests.auth import HTTPBasicAuth
import threading
import time
import random
import pandas as pd
# from dotenv import load_dotenv
import os
# load_dotenv()
# account = os.getenv("test_count")
# password = os.getenv("test_passrword")
#      'sessionid': '4f5nwwiy46mkz7zn3coufj25gc5as06h'
# url = 'http://127.0.0.1:8000/api_food/food/'
# def test_api(url):
# #     headers = {'XSRF-TOKEN': 'Wm3xVpKsbnvXJ96W4js1KgubreRiGIjg',
# #     'sessionid':'uf5wha9r3gx0l1at11tmbyq8hq958rpv'
# # }
#     data = {
#     'food_name': '色柚汁庶', 
#     }

#     response = requests.get(url,data=data,auth=HTTPBasicAuth('root', '123456'))
#     print(response.status_code)
#     print(response.json())

# test_api(url)


# url = "https://api.land.moi.gov.tw/cp/api/BuildingDescription/1.0/QueryByBuildNo"
# data = [{"NO": "01233000", "SEC": "0606", "UNIT": "AD"},{"NO": "04773000", "SEC": "0603", "UNIT": "AD"}]
# datas = json.dumps(data,sort_keys=True)
# res = requests.post(url,data=datas,auth=(account,password))
# res_text = res.text
# print(f"res_text:{res_text}")
# res_text = res_text.replace("\r\n", "")
# res_text = res_text.replace("  ", "")
# res_text = res_text.replace("null", "\"\"")
# print(res_text)

#! logger 寫入練習
# import logging
# # 設定日誌的基本配置
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# # 創建 FileHandler，將日誌寫入到 log.txt 檔案中
# info_handler = logging.FileHandler('infoLog.txt')
# file_handler = logging.FileHandler('log.txt')
# # 設定 FileHandler 的日誌格式
# file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# info_handler.setLevel(logging.INFO)
# info_handler.setFormatter(file_formatter)
# logging.getLogger().addHandler(info_handler)


# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(file_formatter)
# # 將 FileHandler 添加到日誌處理器
# logging.getLogger().addHandler(file_handler)



# def main():
#     logging.debug('這是一個 DEBUG 級別的日誌訊息')
#     logging.info('這是一個 INFO 級別的日誌訊息')
#     logging.warning('這是一個 WARNING 級別的日誌訊息')
#     logging.error('這是一個 ERROR 級別的日誌訊息')
#     logging.critical('這是一個 CRITICAL 級別的日誌訊息')

# if __name__ == "__main__":
#     main()


#! asyncio  異步處理練習
# import asyncio

# async def task1():
#     print("Task 1 started")
#     await asyncio.sleep(2)
#     print("Task 1 completed")

# async def task2():
#     print("Task 2 started")
#     await asyncio.sleep(1)
#     print("Task 2 completed")

# async def main():
#     # 創建任務
#     t1 = asyncio.create_task(task1())
#     t2 = asyncio.create_task(task2())

#     # 等待任務完成
#     await t1
#     await t2

# # 開始事件循環
# asyncio.run(main())



# import asyncio

# async def fetch_url(url):
#     print(f"Fetching {url}")
#     await asyncio.sleep(2)  # 模擬請求延遲
#     print(f"Finished fetching {url}")

# async def main():
#     urls = ["http://example.com", "http://google.com", "http://openai.com"]

#     # 創建任務列表
#     tasks = [fetch_url(url) for url in urls]

#     # 等待所有任務完成
#     await asyncio.gather(*tasks)

# # 開始事件循環
# asyncio.run(main())

#!　多線程練習

# import threading
# import time

# def task1():
#     print("Task 1 started")
#     time.sleep(2)  # 模擬耗時操作
#     print("Task 1 completed")

# def task2():
#     print("Task 2 started")
#     time.sleep(1)  # 模擬耗時操作
#     print("Task 2 completed")

# def main():
#     # 創建兩個線程
#     thread1 = threading.Thread(target=task1)
#     thread2 = threading.Thread(target=task2)

#     # 開始執行線程
#     thread1.start()
#     thread2.start()

#     # 等待兩個線程完成
#     thread1.join()
#     thread2.join()

# # 執行主線程
# main()



# url = 'https://lbor.yeshome.net.tw/tasks/create/transcript/v2/'
# def test_api(res):
#     data = {
#     'token':'399bda52-b0a9-4e59-ace6-29c088b6fd50',
#     'lbkeys': ','.join(res),
#     'priority':96,
#     'system':2,
#     'source':f"KEVIN 義鼎任務"
#     }
#     response = req.post('https://lbor.yeshome.net.tw/tasks/create/transcript/v2/',data=data)
#     print(response.status_code)


# def batch(iterable, n=1):
#     l = len(iterable)
#     for ndx in range(0, l, n):
#         yield iterable[ndx:min(ndx + n, l)]

# df = pd.read_csv("C:/Users/88698/Downloads/南投草屯鎮40142筆.csv")
# print(len(df['lkey']))
# for i in batch(df['lkey'],1000):
#     res = i.tolist()
#     test_api(res)



import requests
import json
import base64
api_url = "http://127.0.0.1:8000/api/create_encryption/"

data = {
    "username": "kevin",
    "password": "s860530321"
}

response = requests.post(api_url, json=data)

if response.status_code == 200:
    try:
        response_data = response.json()
        
        # 检查是否成功获取了encrypted_value
        if "encrypted_value" in response_data:
            print(f"encrypted_value : {response_data.get('encrypted_value', '')}成功！")
        else:
            print("失敗: 無效encrypted_value")
    except json.decoder.JSONDecodeError as e:
        print("錯誤訊息：", str(e))
else:
    print("請求失敗：", response.status_code)

# # 检查是否成功获取了encrypted_value
# if "encrypted_value" in response_data:
#     # 设置API端点
#     api_url = "http://127.0.0.1:8000/api/verify_decryption/"

#     # 提供帐号、密码和解密后的值
#     data = {
#         "username": "kevin",
#         "password": "s860530321",
#         "decrypted_value": response_data.get('encrypted_value', '')  # 使用get方法以避免KeyError
#     }

#     # 发送POST请求
#     response = requests.post(api_url, json=data)
#     # 解析响应
#     try:
#         response_data = response.json()
#         # 检查响应
#         if "message" in response_data and response_data["message"] == "驗證成功":
#             print("驗證成功！")
#         else:
#             print("驗證失敗。")
#     except json.decoder.JSONDecodeError as e:
#         print("錯誤訊息：", str(e))
# else:
#     print("未成功获取encrypted_value。")



# import requests
# import json

# # 设置API端点
# api_url = "http://127.0.0.1:8000/api/verify_decryption/"

# # 提供帐号、密码和解密后的值
# data = {
#     "username": "kevin",
#     "password": "s860530321",
#     "decrypted_value":  base64.b64encode(b'y\x15h\t"\xe4\\\xd4|-5\xee\xf5\x99\xa5\xbad\xad\xee\x7f\xb5}@\x95\x1aJ\x08\x00\xfb\x99\x0f\xba\n\x05t\x1b\xa1\x97j\xa6\xf7\x0b\xc2\xe9\x9bl\xf7f\x02\xce\xdb-\x7f8\x05Z\xf2L\xbc(I\xa7\x00\x86w\xc9\xd7\x86!\x16\xa0\x16m~\x80\xdf\xdb\xed\x10p%Op\xec2<L\x9eS)\xa6O\xbeMo\xa9\xb9\xe2*C@g\xa3\xa1w\x12<\xdf\xb3\xa9\xa3\xa2\x83Q5\x82\x9c\xf8^\x11l\xa09=\x9c\x7f`}\x19\x05\xce\x03\x0f\x9f/\xdcR\x0c\xf0\x9a8:2Y_\x9b#\x1dN\xc1\xa4M]t\xc43\x19\xe1\xca\x90>\x14`*W\xc9\xde\xa9m\xbf\xeec\xa2\xb0\xec\x1f\xef\x04s\xae\xfd]\x81\xb9\xb3\xc6\xc7\x9a&\xf0B\x98\x87\xcb\x86\x01\xa7\xe8\xc6\xf28\x06\x12\xccR\xc9\x9d\x05\xd6^\x1b\xbc\xc9\xc1\xe8\xd1\xcd\xc8\x0b=\xe8\xeb\x9d.\x12\x1cMse\x1c\xe5\x1eO\x08wv$\x8f\xbd@az\xe5N>\x15F\xab\xa6M\r\x9c-\xe4\xb4"').decode('utf-8')
# }

# # 发送POST请求
# response = requests.post(api_url, json=data)

# # 解析响应
# try:
#     response_data = response.json()
#     if "message" in response_data:
#         print(response_data["message"])
#     else:
#         print("未收到有效的响应。")
# except json.decoder.JSONDecodeError as e:
#     print("解析响应时出错：", str(e))


# sql_query ='''
# SELECT
#     AVG(price) AS average_price,
#     MAX(price) AS max_price,
#     MIN(price) AS min_price,
#     ROUND(UNIX_TIMESTAMP(CURTIME(4)) * 1000) AS ts
# FROM
#     products;
# '''

# import requests
# import json

# # 设置你的API端点
# api_url = "http://127.0.0.1:8000/api/sql_test/"

# credentials = {
#     "username": "3q4I9rKfid",
#     "password": "6evZXtIg6X"
# }

# # 构建SQL查询
# sql_query = """
# SELECT
#     AVG(price) AS average_price,
#     MAX(price) AS max_price,
#     MIN(price) AS min_price,
#     ROUND(STRFTIME('%s', 'now') * 1000) AS ts
# FROM
#     encryption_verification_product;
# """

# # 构建API请求数据
# api_data = {
#     "username": credentials["username"],
#     "password": credentials["password"],
#     "sql": sql_query
# }

# # 发送API请求
# response = requests.post(api_url, json=api_data)

# # 解析API响应
# if response.status_code == 200:
#     response_data = response.json()
#     if "message" in response_data:
#         print(response_data["message"],response_data["results"])
#     else:
#         print("測試失敗")
# else:
#     print("失敗：", response.status_code)



#!　綠界金流encode
import urllib.parse
import hashlib
def custom_urlencode(input_str, char_to_encode):
    encoded_chars = []
    
    
    for char in input_str:
        if char in char_to_encode:
            encoded_chars.append(char)
        elif char == " ":
            encoded_chars.append("+")
        elif char == "/":
            encoded_chars.append("%2f")
        elif char == "\\":
            encoded_chars.append("%5c")
        else:
            encoded_chars.append(urllib.parse.quote(char))
    res = ''.join(encoded_chars)
    lowercase_data = res.lower()
    hash_obj = hashlib.sha256()
    hash_obj.update(lowercase_data.encode('utf-8'))
    hash_value = hash_obj.hexdigest()
    check_mac_value = hash_value.upper()
    return check_mac_value

input_str = "HashKey=pwFHCqoQZGmho4w6&ChoosePayment=ALL&EncryptType=1&ItemName=Apple iphone 15&MerchantID=3002607&MerchantTradeDate=2023/03/12 15:30:23&MerchantTradeNo=ecpay20230312153023&PaymentType=aio&ReturnURL=https://www.ecpay.com.tw/receive.php&TotalAmount=30000&TradeDesc=促銷方案&HashIV=EkRm7iFT261dpevs"
char_to_encode = "–_.!*()"
encoded_str = custom_urlencode(input_str, char_to_encode)
print(encoded_str)