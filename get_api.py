from dotenv import load_dotenv
import requests as req
import json
from shutil import copy
import os
import schedule
import subprocess
import sys
import time
import shutil
from apscheduler.schedulers.blocking import BlockingScheduler
from pathlib import Path
import re
def get(url):

    headers = {
    'Content-Type': 'application/json',
    'token': '36df4fa17a6e4d9e8540d490c0cc9658',
    }

    response = req.post(url,data=headers)
    if response.status_code == 200:
        if 'application/json' in response.headers.get('Content-Type'):
            datas = response.json()
            if datas['status'] == 'OK':
                for data in datas['task_list']:
                    print('取得任務')
                    jsonfile ={}
                    jsonfile["QueryItem"]=data["lbkey"]
                    jsonfile["hn"]=data["hn"]
                    jsonfile["pw"]=data["pw"]
                    jsonfile["QueryParameters"]={"taskid":data["taskid"]}
                    file_name = f"{data['lbkey']}.json"
                    if data['lbkey'] == '':
                        print('無效lbkey')
                    else:
                        if not os.path.exists(f"C:/Users/88698/AppData/Local/Temp/YesQT2/New/{file_name}"):
                            print(file_name)
                            with open(f"C:/Users/88698/AppData/Local/Temp/YesQT2/New/{file_name}", 'w') as f:
                                f.write('{}')
                        with open(f"C:/Users/88698/AppData/Local/Temp/YesQT2/New/{file_name}", "w") as f:
                            json.dump(jsonfile,f,indent=6)
                print("任務完成")
            else:
                print('未取得任務')
        else:
            print('不是JSON格式。')
    else:
        print('API無回應')


def done():
    try:
        info_path = f"C:/Users/88698/AppData/Local/Temp/YesQT2/Results"
        file_path = 'C:/Users/88698/AppData/Local/Temp/YesQT2/Results'
        save_path = 'C:/Users/88698/AppData/Local/Temp/YesQT2/done'
        for data in Path(file_path).iterdir():
            if data.name != '.DS_Store':
                old_file_path = file_path+'/'+data.name
                new_file_path = save_path+'/'+data.name
                if not os.path.exists(new_file_path):
                    os.mkdir(new_file_path)
        for firPath,dirNames, fileNames in os.walk(info_path):
            for i in fileNames:
                with open(os.path.join(firPath,i), newline='') as jsonfile:
                    data = json.load(jsonfile)
                    pattern = r'\d+'
                    result = re.findall(pattern, json.dumps(data['QueryParameters']))
                    url = "https://diablo-test.yeshome.net.tw/csapis/feedback/"
                    headers = {
                    'Content-Type': 'application/json',
                    'token': 'b43cda82b15f4d33adcae8f28d4a8e98',
                    "taskid":result[0],
                    "result_json":json.dumps(data)
                    }
                    response = req.post(url,data=headers)
                    
                    if response.status_code == 200:
                        print("ok")
                    else:
                        print(response.text)
                    
        file_path = 'C:/Users/88698/AppData/Local/Temp/YesQT2/Results'
        save_path = 'C:/Users/88698/AppData/Local/Temp/YesQT2/done'
        for data in Path(file_path).iterdir():
            if data.name != '.DS_Store':
                old_file_path = file_path+'/'+data.name
                new_file_path = save_path+'/'+data.name
                if not os.path.exists(new_file_path):
                    os.mkdir(new_file_path)
                pathDir = os.listdir(old_file_path)
                for file_name in pathDir:
                    if os.path.exists(new_file_path + '/' + file_name):
                        os.remove(new_file_path + '/' + file_name)
                    if not os.path.exists(file_name):
                        os.rename(old_file_path + '/' + file_name,
                                new_file_path + '/' + file_name)
                    else:
                        os.remove(new_file_path + '/' + file_name)
                        os.rename(old_file_path + '/' + file_name,
                                new_file_path + '/' + file_name)
    except Exception as e:
        print(e)
done()

# 測試中關閉

# schedule.every(1).seconds.do(get,url='https://diablo-test.yeshome.net.tw/csapis/get_task/')

# while True:
#     schedule.run_pending()
#     done()
    # time.sleep(10)