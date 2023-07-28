import tkinter as tk
import myTools as mt
import pymysql
import pandas as pd
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import os
import json
from dotenv import load_dotenv
import logging
load_dotenv()
logging.basicConfig(filename='example.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# 預估任務
def log_message(messge):
    return list_var.set(logging.info(messge))

def task_estimate():
    lb_key=entry1.get()
    e_url = "https://diablo-test.yeshome.net.tw/csapis/eval/"
    data = {
        'token':'b43cda82b15f4d33adcae8f28d4a8e98',
        'action':'3',
        'lbkey':lb_key,
        'hn': os.getenv("hn"),
        'pw': os.getenv("pw")
    }
    response = requests.post(e_url,data=data)
    if response.status_code == 200:
        content =response.text
        # lbkey_list = f"{json.loads(content)['status']},taskid:{json.loads(content)['taskid']}"
        # print(lbkey_list['lbkey'])
        log_message(f"預估任務:{json.loads(content)['lbkey']},taskid:{json.loads(content)['taskid']}")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(f"預估任務:{json.loads(content)['lbkey']},taskid:{json.loads(content)['taskid']}")
    else:
        label0.config(text='只需要lbkey!',fg='red')
        log_message(f"預估任務:未填入lbkey")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return "只需要lbkey!"

#查詢列表
def tasklist():
    lb_key=entry1.get()
    e_url = "https://diablo-test.yeshome.net.tw/csapis/eval/"
    data = {
        'token':'b43cda82b15f4d33adcae8f28d4a8e98',
        'action':'4',
        'lbkey':lb_key,
        'hn': os.getenv("hn"),
        'pw': os.getenv("pw")
    }
    response = requests.post(e_url,data=data)
    if response.status_code == 200:
        content =response.text
        # lbkey_list = [[f"{json.loads(content)['status']},taskid:{json.loads(content)['taskid']}"]]
        log_message(f"msg:{json.loads(content)['msg']},taskid:{json.loads(content)['lbkey']}")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(f"msg:{json.loads(content)['msg']},taskid:{json.loads(content)['lbkey']}")
    else:
        label0.config(text='只需要lbkey!',fg='red')
        log_message(f"查詢列表:未填入lbkey")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return "只需要lbkey!"
# 一鍵更新的資料
def one_click():
    lb_key=entry1.get()
    e_url = "https://diablo-test.yeshome.net.tw/csapis/eval/"
    data = {
        'token':'b43cda82b15f4d33adcae8f28d4a8e98',
        'action':'3',
        'lbkey':lb_key,
        'hn': os.getenv("hn"),
        'pw': os.getenv("pw")
    }
    e_response = requests.post(e_url,data=data)
    if e_response.status_code == 200:
        content =e_response.text
        datas = {
        'Content-Type': 'application/json',
        'token': '36df4fa17a6e4d9e8540d490c0cc9658',
        'action':'5',
        'taskid':json.loads(content)['taskid'],
        'hn':os.getenv("hn"),
        'pw':os.getenv("pw")
        }
        url = "https://diablo-test.yeshome.net.tw/csapis/task/"
        t_response = requests.post(url,data=datas)
        t_content =t_response.text
        datas = {
        'Content-Type': 'application/json',
        'token': '36df4fa17a6e4d9e8540d490c0cc9658',
        'taskid':json.loads(t_content)['taskid']
        }
        url = "https://diablo-test.yeshome.net.tw/csapis/status/"
        response = requests.post(url,data=datas)
        res = response.text
        info = [[f"{json.loads(res)['status']}"]]
        log_message(f"一鍵完成:{json.loads(res)['lbkey']},taskid:{json.loads(res)['taskid']}")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(f"一鍵完成:{json.loads(res)['lbkey']},taskid:{json.loads(res)['taskid']}")
    else:
        log_message(f"一鍵完成:未填入lbkey")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        label0.config(text='只需要lbkey!',fg='red')
        
        
# 建立任務
def task_creat():
    # lb_key=entry1.get()
    taskid = entry2.get()
    datas = {
    'Content-Type': 'application/json',
    'token': '36df4fa17a6e4d9e8540d490c0cc9658',
    'action':'5',
    'taskid':taskid,
    'hn':os.getenv("hn"),
    'pw':os.getenv("pw")
    }
    url = "https://diablo-test.yeshome.net.tw/csapis/task/"
    t_response = requests.post(url,data=datas)
    if t_response.status_code == 200:
        t_content =t_response.text
        # lbkey_list = f"{json.loads(t_content)['status']},taskid:{json.loads(t_content)['taskid']}"
        log_message(f"建立任務:{json.loads(t_content)['status']},taskid:{json.loads(t_content)['taskid']}")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(f"建立任務:{json.loads(t_content)['status']},taskid:{json.loads(t_content)['taskid']}")
    else:
        log_message(f"建立任務:未輸入預估任務的taskid")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        label0.config(text="只需輸入預估任務的taskid",fg='red')

def task_check():
    taskid = entry2.get()
    datas = {
    'Content-Type': 'application/json',
    'token': '36df4fa17a6e4d9e8540d490c0cc9658',
    'taskid':taskid
    }
    url = "https://diablo-test.yeshome.net.tw/csapis/status/"
    response = requests.post(url,data=datas)
    if response.status_code == 200:
        res=response.text
        # info = f"{json.loads(res)['status']}"
        log_message(f"任務查詢:{json.loads(res)['lbkey']},taskid:{json.loads(res)['taskid']}")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(f"任務查詢:{json.loads(res)['lbkey']},taskid:{json.loads(res)['taskid']},status:{json.loads(res)['status']}")
    else:
        log_message(f"任務查詢:未輸入建立任務的taskid")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        label0.config(text="只需輸入建立任務的taskid",fg='red')
        

def one_task():
    db_settings = {
            "host":"104.yeshome.net.tw",
            "port":3306,
            "user":os.getenv("DEFAULT_DATABASE_USER"),
            "password":os.getenv("DEFAULT_DATABASE_PASSWORD"),
            "db":"lbor_v2",
            "charset":"utf8mb4"
        }
    try:
        conn = pymysql.connect(**db_settings)

        with conn.cursor() as cursor:
            command = """SELECT lbkey FROM lbor_v2.tasks_transcripttasks a WHERE state = '3' OR (state = '1' AND TIMESTAMPDIFF(HOUR,create_time,NOW()) >=5) LIMIT 1"""
            cursor.execute(command)
            data = cursor.fetchone()
            e_url = "https://diablo-test.yeshome.net.tw/csapis/eval/"
            data = {
                'token':'b43cda82b15f4d33adcae8f28d4a8e98',
                'action':'3',
                'lbkey':data[0],
                'hn': os.getenv("hn"),
                'pw': os.getenv("pw")
            }
            e_response = requests.post(e_url,data=data)
            if e_response.status_code == 200:
                content =e_response.text
                datas = {
                'Content-Type': 'application/json',
                'token': '36df4fa17a6e4d9e8540d490c0cc9658',
                'action':'5',
                'taskid':json.loads(content)['taskid'],
                'hn':os.getenv("hn"),
                'pw':os.getenv("pw")
                }
                url = "https://diablo-test.yeshome.net.tw/csapis/task/"
                t_response = requests.post(url,data=datas)
                t_content =t_response.text
                log_message(f"單筆任務:{json.loads(t_content)['status']},taskid:{json.loads(t_content)['taskid']}")
                with open('example.log', 'r') as log_file:
                    log_contents = log_file.read()
                    text_box.insert(tk.END, log_contents)
            return list_var.set(f"單筆任務:{json.loads(t_content)['taskid']}")
    except Exception as ex:
        log_message(f"資料庫連線失敗")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(ex)

def five_task():
    db_settings = {
            "host":"104.yeshome.net.tw",
            "port":3306,
            "user":os.getenv("DEFAULT_DATABASE_USER"),
            "password":os.getenv("DEFAULT_DATABASE_PASSWORD"),
            "db":"lbor_v2",
            "charset":"utf8mb4"
        }
    try:
        conn = pymysql.connect(**db_settings)
    
        with conn.cursor() as cursor:
            command = """SELECT lbkey FROM lbor_v2.tasks_transcripttasks a WHERE state = '3' OR (state = '1' AND TIMESTAMPDIFF(HOUR,create_time,NOW()) >=5) LIMIT 5"""
            cursor.execute(command)
            data = cursor.fetchall()
            lbkeys = []
            for t in data:
                string = t[0]  # assuming each tuple contains only one string element
                lbkeys.append(string)
            for lbkey in lbkeys:
                e_url = "https://diablo-test.yeshome.net.tw/csapis/eval/"
                data = {
                    'token':'b43cda82b15f4d33adcae8f28d4a8e98',
                    'action':'3',
                    'lbkey':lbkey,
                    'hn': os.getenv("hn"),
                    'pw': os.getenv("pw")
                }
                e_response = requests.post(e_url,data=data)
                if e_response.status_code == 200:
                    content =e_response.text
                    datas = {
                    'Content-Type': 'application/json',
                    'token': '36df4fa17a6e4d9e8540d490c0cc9658',
                    'action':'5',
                    'taskid':json.loads(content)['taskid'],
                    'hn':os.getenv("hn"),
                    'pw':os.getenv("pw")
                    }
                    url = "https://diablo-test.yeshome.net.tw/csapis/task/"
                    t_response = requests.post(url,data=datas)
                    t_content =t_response.text
                    # info = f"{json.loads(t_content)['status']}"
                    log_message(f"多筆任務:{json.loads(t_content)['status']},taskid:{json.loads(t_content)['taskid']}")
                    with open('example.log', 'r') as log_file:
                        log_contents = log_file.read()
                        text_box.insert(tk.END, log_contents)
                    
            return list_var.set(f"多筆任務:{json.loads(t_content)['status']},taskid:{json.loads(t_content)['taskid']}")
    except Exception as ex:
        log_message(f"資料庫連線失敗")
        with open('example.log', 'r') as log_file:
            log_contents = log_file.read()
            text_box.insert(tk.END, log_contents)
        return list_var.set(ex)
    
def address_task():
        def get_all_code(type):
            headers = {'Authorization': 'token fde85ab9e07f128e90d63091aca86f1e9a9d139d'}
            url = f'https://lbor.wsos.com.tw/common/car/get_all_code/?select_type={type}'
            code_datas = requests.get(url, headers=headers)
            code_datas = code_datas.json()
            return code_datas
        def get_lbkey(code_datas):
            task_city = entry3.get()
            task_region = entry4.get()
            task_section = entry5.get()
            task_lb = entry6.get()
            city_list = []
            print(task_city=='')
            if task_city == '' or task_region == '' or task_section == '' or task_lb == '':
                return list_var.set('請填寫縣市，行政區，地段名，地建號')
            if '市' not in task_city:
                return list_var.set('請輸入完整縣市名稱，如:台北市')
            if '台' in task_city:
                rename = task_city.replace('台', '臺')
                city_list.append(rename)
            else:
                city_list.append(task_city)
            lb_keys = []
            city_name = city_list[0]
            area_name = task_region
            region_name = task_section
            s = task_lb
            print(city_name)
            print(area_name)
            print(region_name)
            print(s)
            if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
                lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{s}'
                lb_keys.append(lb_key)
            else:
                lb_keys.append('None')
                return list_var.set('查無此地建號')
            return lb_keys
        code_datas = get_all_code(1)
        return list_var.set(get_lbkey(code_datas))
def clear():
    b = tk.StringVar()
    b.set('')               # 設定變數 b 為空字串
    entry1.delete(0,'end')
    entry2.delete(0,'end')
    entry3.delete(0,'end')
    entry4.delete(0,'end')
    entry5.delete(0,'end')
    entry6.delete(0,'end') # 清空輸入欄位內容


table_str='''CREATE TABLE "lbkey" (
"lbkey" TEXT,
"id" TEXT,
"state" TEXT,
"process_state" TEXT,
"task_time" TEXT,
"log_time"
);'''


conn1=None
cursor1=None
db_name='lbkey.db'
open('example.log', 'w').close()
win=tk.Tk()
list_var=tk.StringVar()
list_var.set([])
win.title('調謄本任務')
frame1=tk.Frame(win,bg='white')
frame1.pack(fill='x')
frame2=tk.Frame(win,bg='white')
frame2.pack(fill='x')
frame3=tk.Frame(win,bg='white')
frame3.pack(fill='x')
frame4=tk.Frame(win,bg='white')
frame4.pack(fill='x')
text_box = tk.Text(win)
text_box.pack()



label0=tk.Label(frame1,text='請輸入lbkey:',font=('Arial',12),bg='black',fg='white',anchor='w')
label0.pack(fill='x')
label1=tk.Label(frame2,text='地建號:',font=('Airal',16),fg='black',bg='white')
label1.grid(row=1,column=0,padx=10)
entry1=tk.Entry(frame2,bg='thistle1',fg='black',font=('Arial',16),borderwidth=3)
entry1.grid(row=1,column=1,pady=5,padx=10)
label2=tk.Label(frame2,text='工廠任務id:',font=('Airal',16),fg='black',bg='white')
label2.grid(row=2,column=0,padx=10)
entry2=tk.Entry(frame2,bg='thistle1',fg='black',font=('skyblue',16),borderwidth=3)
entry2.grid(row=2,column=1,pady=5,padx=10)
label3=tk.Label(frame2,text='縣市:',font=('Airal',16),fg='black',bg='white')
label3.grid(row=1,column=3,padx=10)
entry3=tk.Entry(frame2,bg='thistle1',fg='black',font=('skyblue',16),borderwidth=3)
entry3.insert(0,"例如:台北市")
entry3.grid(row=1,column=4,pady=5,padx=10)
label4=tk.Label(frame2,text='地區:',font=('Airal',16),fg='black',bg='white')
label4.grid(row=2,column=3,padx=10)
entry4=tk.Entry(frame2,bg='thistle1',fg='black',font=('skyblue',16),borderwidth=3)
entry4.insert(0,"例如:板橋區")
entry4.grid(row=2,column=4,pady=5,padx=10)
label5=tk.Label(frame2,text='段小段:',font=('Airal',16),fg='black',bg='white')
label5.grid(row=3,column=3,padx=10)
entry5=tk.Entry(frame2,bg='thistle1',fg='black',font=('skyblue',16),borderwidth=3)
entry5.insert(0,"例如:鷺江段")
entry5.grid(row=3,column=4,pady=5,padx=10)
label6=tk.Label(frame2,text='地建號',font=('Airal',16),fg='black',bg='white')
label6.grid(row=4,column=3,padx=10)
entry6=tk.Entry(frame2,bg='thistle1',fg='black',font=('skyblue',16),borderwidth=3)
entry6.insert(0,"例如:03187-000 or 1206-0000")
entry6.grid(row=4,column=4,pady=5,padx=10)


button1=tk.Button(frame3,text='任務預估(lbkey)',font=('Arial',15),command=task_estimate,activeforeground='blue')
button1.grid(row=0,column=0,padx=20,pady=5)
button2=tk.Button(frame3,text='任務建立(taskid)',font=('Arial',15),command=task_creat,activeforeground='blue')
button2.grid(row=0,column=1,padx=20,pady=5)
button3=tk.Button(frame3,text='任務查詢(taskid)',font=('Arial',15),command=task_check,activeforeground='blue')
button3.grid(row=0,column=2,padx=20,pady=5)
button4=tk.Button(frame3,text='一鍵完成(lbkey)',font=('Arial',15),command=one_click,activeforeground='blue')
button4.grid(row=0,column=3,padx=20,pady=5)
button5=tk.Button(frame3,text='查工廠建任務(單筆)',font=('Arial',15),command=one_task,activeforeground='blue')
button5.grid(row=1,column=0,padx=20,pady=5)
button6=tk.Button(frame3,text='查工廠建任務(5筆)',font=('Arial',15),command=five_task,activeforeground='blue')
button6.grid(row=1,column=1,padx=20,pady=5)    
button7=tk.Button(frame3,text='查詢列表',font=('Arial',15),command=tasklist,activeforeground='blue')
button7.grid(row=1,column=2,padx=20,pady=5)
button8=tk.Button(frame3,text='手動輸入查詢',font=('Arial',15),command=address_task,activeforeground='blue')
button8.grid(row=1,column=3,padx=20,pady=5)
btn2 = tk.Button(frame3, text='清除', command=clear,font=('Arial',15))  # 放入清空按鈕，點擊後執行 clear 函式
btn2.grid(row=3,column=0,padx=20,pady=5)

sb=tk.Scrollbar(frame4)
sb.pack(side='right',fill='y')
sb1=tk.Scrollbar(frame4,orient='horizontal')
sb1.pack(side='bottom',fill='x')


listbox=tk.Listbox(frame4,listvariable=list_var,font=('Arial',20),bg='OliveDrab1',fg='blue2'\
,yscrollcommand=sb.set,xscrollcommand=sb1.set)
listbox.pack(fill='x')
sb.config(command=listbox.yview)
sb1.config(command=listbox.xview)
win.mainloop()