import requests
import pdfplumber
import pandas as pd
import re
import logging
import sys
import os
import csv
import datetime
# from handle_errors import take_out_duan_little_duan, check_land_number
logger = logging.getLogger(__name__)
folder_path = '/Users/shane/Desktop/work/python/tpkonsale_scraping/all_pdf'

def jcBuildingSm(sm_original):
    sm_extra = ''
    sm_key = None
    if sm_original:
        sm_original = sm_original.replace('\n', '')
        if '增' in sm_original:
            sm_extra = '增建'
        elif '暫' in sm_original:
            sm_extra = '暫編'
        elif '棟' in sm_original:
            sm_extra = '棟次'
            # 88棟次3
            sm_original = sm_original[:sm_original.index("棟")+1]
        elif '地上' in sm_original:
            sm_extra = '地上物'
        elif '封' in sm_original:
            sm_extra = '查封'
        elif '假' in sm_original:
            sm_extra = '假扣押'
        elif '未' in sm_original:
            sm_extra = '未辦登記查封'

        word = dict(zip(map(ord, u'增建暫編棟次()（）.地上物查封號假未'),
                        map(ord, u'                   ')))

        sm_original = sm_original.translate(word)
        sm_original = sm_original.replace(' ', '')

        if sm_original.find('-') >= 0:
            sm_split = sm_original.split('-')
            sm_key = "{}-{}".format(sm_split[0].zfill(5), sm_split[1].zfill(3))
        else:
            sm_key = "{}-000".format(sm_original.zfill(5))
    return sm_extra, sm_key


def check_area_name(city_name, area_name):
    if city_name in ['嘉義市', '新竹市']:
        # 嘉義市沒有東區 行政區只有嘉義市
        return city_name
    if not area_name:
        return None
    area_name = area_name.replace('臺', '台')
    if area_name[-1] in '鄉鎮市區':
        return area_name
    if city_name in ['臺北市', '臺中市', '桃園市', '新北市', '高雄市', '臺南市', '基隆市']:
        # 直轄市
        return area_name + '區'
    return area_name


def get_all_code(type=0):
    headers = {'Authorization': 'token fde85ab9e07f128e90d63091aca86f1e9a9d139d'}
    url = f'https://lbor.wsos.com.tw/common/car/get_all_code/?select_type={type}'
    code_datas = requests.get(url, headers=headers)
    code_datas = code_datas.json()
    return code_datas


def wrap_replace(string):
    if string:
        return string.replace('\n', '').replace('段段', '段').replace(' ', '')
    return ''


def check_land_number(region_name, data, sm_original):
    if region_name == "東林段":
        sm_original = str(data[0][4])
        return sm_original
    return sm_original


# 將list轉緩成string


def take_out_space(string):
    a = []
    for x in string:
        if x != " ":
            a.append(x)
    new_string = ''.join(a)
    return new_string


def parserPDF(lists_df, code_datas):
    error_count = 0
    data_dict = {}
    for table_list in lists_df:
        try:
            owner = table_list[0][0][table_list[0][0].index('：')+1:]
        except:
            owner = table_list[0][0][table_list[0][0].index('人:')+2:]
        # # # 分割細項 去掉標題三行 用編號判斷起始點
        split_num = 3
        for num, talist in enumerate(table_list):
            try:
                int(talist[0])
                split_num = num
                break
            except:
                pass
        # # 判斷有沒有備考 沒的話 用1行切割
        prepare = 2
        if len(table_list) > 5 and ('備' not in str(table_list[split_num + 1][1] or '')):
            prepare = 1
        """
        以下的if else 看似很複雜,也許有辦法簡化,但是是為了很多奇怪的可能,所以才將他分別出來的,若要移除
        ,建議還是將原版留好,可能當前測試的ＰＤＦ可以,但是其他的ＰＤＦ就會出現異常了
        """
        # 因為土這個字有可能出現在table_list[1][1] 或是table_list[1][2] 中因此改寫成,這種方式來處理異常
        # 為什麼要用a=0來改寫是因為,如果沒有用a=0來改寫會進入table_list[1][1] 裏面,如果頁面出現切割的情況會找不到資料
        # all_serial_number = [idx for idx, row in enumerate(
        #     table_list[1:], 1) if row[0] is not None and wrap_replace(row[0][0]) == "編"]
    #     # 為了處理PDF有兩頁的時候會出現的問題,因此再新增一個來處理
        if '建' not in table_list[1][1] and '地 \n \n \n目' not in table_list[1] and '備\n註'not in table_list[-1] and '備 \n註'not in table_list[-1]:
            data_list = [table_list[split_num:][i:i+prepare]
                         for i in range(0, len(table_list[split_num:]), prepare)]
            if str(len(all_serial_number)) == '1':
                try:
                    if '土' in table_list[1][1]:
                        a = 0
                except:
                    if '土' in table_list[1][2]:
                        a = 0
                if a == 0:
                    '''
                        表格欄位介紹

                        不常見: 長度8
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 地號 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價

                        常見: 長度9
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價

                        不常見: 長度10
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價 ｜ 保證金額

                        不常見: 長度11  (宜蘭縣)
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 使用地類別 ｜ 使用分區 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價 ｜

                        不常見: 長度12  (彰化縣)
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 使用地類別 ｜ 使用分區 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價 ｜ 保證金額

                        '''
                    # print(data_list)
                    # for data in data_list:
                    #     data[0] = list(
                    #         filter(lambda x: x is not None, data[0]))
                    # print(data[0])
                    # print(data_list)
                    for x in range(0, len(data_list)):
                        # 這行的目的主要是為了找出,如果data_list內有None的可能在排把他排除
                        # print(data_list[x][0][0])
                        # print(table_list[2])
                        if data_list[x][0][0] == None:
                            continue
                        if '編' in data_list[x][0][0]:
                            start_serial_number = x
                        if '點' in data_list[x][0][0]:
                            start_serial_number = x
                        if '點交' in data_list[x][0][0]:
                            start_serial_number = x
                            break
                        if '備' in data_list[x][0][0]:
                            start_serial_number = x
                    # print(start_serial_number)
                    for x in range(0, start_serial_number):
                        # print(data_list[x][0][4])
                        data_list[x][0] = list(
                            filter(lambda x: x is not None, data_list[x][0]))
                        # print(data_list[x][0])
                        city_name = wrap_replace(data_list[x][0][1])
                        area_name = wrap_replace(data_list[x][0][2])
                        region3 = wrap_replace(data_list[x][0][3])
                        # print(city_name, area_name, region3)
                        if city_name == '台北':
                            city_name = "臺北市"
                        city_name = wrap_replace(city_name)
                        # 合併段小段
                        region3 = wrap_replace(region3)
                        if region3 == None:
                            continue
                        # 如果他沒有給他段,我幫他加上
                        if region3[-1] != '段':
                            region3 = region3+'段'
                        region4 = ''
                        # print(len(data_list[x][0]))
                        region4 = str(data_list[x][0][4] or '')
                        # print(region4)
                        if region4 and region4[-2:] != '小段':
                            region4 += '小段'
                        else:
                            region3
                        region3 = region3.replace(
                            '豬朥束', '猪朥束')
                        region_name = region3 + region4
                        # print(region_name)
                        # if '小段' or '小\n段'not in table_list[2]:
                        #     region_name = region3
                        # print(region_name)
                        # 取代數字小段
                        word = dict(zip(map(ord, u'1234567890'),
                                    map(ord, u'一二三四五六七八九零')))
                        region_name = region_name.translate(word)
                        # 把跳行符號跟斷斷去除
                        region_name = wrap_replace(region_name)
                        # 將文字中的空格剔除
                        region_name = take_out_space(region_name)
                        # if '小段' not in table_list[2]:
                        #     sm_original = wrap_replace(data_list[x][0][4])
                        #     if sm_original == '':
                        #         sm_original = data_list[x][0][5]
                        # elif len(data_list[x][0]) in [8]:
                        #     sm_original = wrap_replace(data_list[x][0][5])
                        # else:
                        #     sm_original = wrap_replace(data_list[x][0][6])
                        sm_original = wrap_replace(data_list[x][0][5])
                        # print(sm_original)
                        # 確認過有東西
                        sm_original = check_land_number(
                            region_name, data_list[x], sm_original)
                        # print(sm_original)
                        sm_re = re.compile(r'^(\d*)[-之]?(\d*)號?(.*)')
                        sm_match = sm_re.match(sm_original)
                        s = sm_match[1]
                        m = sm_match[2]
                        area_name = check_area_name(city_name, area_name)
                        area_name = wrap_replace(area_name)
                        # print(city_name, area_name, region_name)
                        if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
                            # lb_key = []
                            lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{s.zfill(4)}-{m.zfill(4)}'
                        # print(lb_key)
                        else:
                            # print('沒有對到地號')
                            logger.info(
                                f'{city_name} {area_name} {region_name} 無比對到地號')
                            error_count += 1
                            continue
                        if len(data_list[x][0]) in [8]:
                            # 面積
                            m2 = data_list[x][0][5]
                            # 權力範圍
                            right_area = wrap_replace(data_list[0][6])
                            # 最低拍賣價格
                            money_down = data_list[x][0][7]
                            # print(money_down)
                        elif len(data_list[x][0]) in [9, 10]:
                            if '小段' not in table_list[1]:
                                if data_list[x][0][4] == '':
                                    # 面積
                                    m2 = data_list[x][0][6]
                                    # 權力範圍
                                    right_area = wrap_replace(
                                        data_list[x][0][7])
                                    # 最低拍賣價格
                                    money_down = data_list[x][0][8]
                                else:
                                    # 面積
                                    m2 = data_list[x][0][5]
                                    # 權力範圍
                                    right_area = wrap_replace(
                                        data_list[x][0][6])
                                    # 最低拍賣價格
                                    money_down = data_list[x][0][7]
                            else:
                                # 面積
                                m2 = data_list[x][0][6]
                                # 權力範圍
                                right_area = wrap_replace(data_list[x][0][7])
                                # 最低拍賣價格
                                money_down = data_list[x][0][8]
                        elif len(data_list[x][0]) in [11, 12]:
                            # 面積
                            m2 = data_list[x][0][8]
                            # 權力範圍
                            right_area = wrap_replace(data_list[x][0][9])
                            # 最低拍賣價格
                            money_down = data_list[x][0][10]
                        else:
                            print(
                                data_list[x], '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@面積 欄位長度')
                        #! 組資料
                        location = city_name+area_name+region_name + sm_original + '地號'
                        data_dict[location] = {
                            'lbkey': lb_key,
                            'owner': owner,
                            'location': location,
                            'location_number': None,
                            'door_number': None,
                            'details': f'{m2} {right_area} {money_down}',
                            # 'extra': extra
                        }
            else:
                # print(table_list)
                try:
                    if '土' in table_list[1][1]:
                        a = 0
                except:
                    if '土' in table_list[1][2]:
                        a = 0
                if a == 0:
                    '''
                        表格欄位介紹

                        不常見: 長度8
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 地號 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價

                        常見: 長度9
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價

                        不常見: 長度10
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價 ｜ 保證金額

                        不常見: 長度11  (宜蘭縣)
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 使用地類別 ｜ 使用分區 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價 ｜

                        不常見: 長度12  (彰化縣)
                        編號 ｜ 縣市 ｜ 鄉鎮市區 ｜ 段 ｜ 小段 ｜ 地號 ｜ 使用地類別 ｜ 使用分區 ｜ 面積 ｜ 權利範圍 ｜ 最低拍賣價 ｜ 保證金額

                        '''
                    # print(data_list)
                    for data in data_list:
                        data[0] = list(
                            filter(lambda x: x is not None, data[0]))
                        if '備' in data[0][0]:
                            continue
                        if '點' in data[0][0]:
                            continue
                        if '使' in data[0][0]:
                            continue
                        if '附' in data[0][0]:
                            continue
                        print(data[0])
                        # city_name = data[0][1]
                        # if city_name == '台北':
                        #     city_name = "臺北市"
                        # city_name = wrap_replace(city_name)
                        # area_name = data[0][2]

                        # 合併段小段
                        # region3 = data[0][3]
        #                 region3 = wrap_replace(region3)
        #                 # 如果他沒有給他段,我幫他加上
        #                 if region3[-1] != '段':
        #                     region3 = region3+'段'
        #                 region4 = ''
        #                 if len(data[0]) not in [8]:
        #                     region4 = str(data[0][4] or '')
        #                     if region4 and region4[-2:] != '小段':
        #                         region4 += '小段'
        #                     else:
        #                         region3
        #                     region3 = region3.replace(
        #                         '豬朥束', '猪朥束')
        #                     region_name = region3 + region4
        #                 if '小段' not in table_list[1]:
        #                     region_name = region3
        #                 # 取代數字小段
        #                 word = dict(zip(map(ord, u'1234567890'),
        #                             map(ord, u'一二三四五六七八九零')))
        #                 region_name = region_name.translate(word)
        #                 # print(region_name)
        #                 # 把跳行符號跟斷斷去除
        #                 region_name = wrap_replace(region_name)
        #                 # 將文字中的空格剔除
        #                 region_name = take_out_space(region_name)
        #                 # print(region_name)
        #                 if '小段' not in table_list[1]:
        #                     sm_original = wrap_replace(data[0][4])
        #                     if sm_original == '':
        #                         sm_original = data[0][5]
        #                 elif len(data[0]) in [8]:
        #                     sm_original = wrap_replace(data[0][4])
        #                 else:
        #                     sm_original = wrap_replace(data[0][5])
        #                 # print(sm_original)
        #                 # 確認過有東西
        #                 sm_original = check_land_number(
        #                     region_name, data, sm_original)
        #                 # print(sm_original)
        #                 sm_re = re.compile(r'^(\d*)[-之]?(\d*)號?(.*)')
        #                 sm_match = sm_re.match(sm_original)
        #                 s = sm_match[1]
        #                 m = sm_match[2]
        #                 area_name = check_area_name(city_name, area_name)
        #                 area_name = wrap_replace(area_name)
        #                 if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
        #                     # lb_key = []
        #                     lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{s.zfill(4)}-{m.zfill(4)}'
        #                 else:
        #                     # print('沒有對到地號')
        #                     logger.info(
        #                         f'{city_name} {area_name} {region_name} 無比對到地號')
        #                     error_count += 1
        #                     continue
        #                 if len(data[0]) in [8]:
        #                     # 面積
        #                     m2 = data[0][5]
        #                     # 權力範圍
        #                     right_area = wrap_replace(data[0][6])
        #                     # 最低拍賣價格
        #                     money_down = data[0][7]
        #                     # print(money_down)
        #                 elif len(data[0]) in [9, 10]:
        #                     if '小段' not in table_list[1]:
        #                         if data[0][4] == '':
        #                             # 面積
        #                             m2 = data[0][6]
        #                             # 權力範圍
        #                             right_area = wrap_replace(data[0][7])
        #                             # 最低拍賣價格
        #                             money_down = data[0][8]
        #                         else:
        #                             # 面積
        #                             m2 = data[0][5]
        #                             # 權力範圍
        #                             right_area = wrap_replace(data[0][6])
        #                             # 最低拍賣價格
        #                             money_down = data[0][7]
        #                     else:
        #                         # 面積
        #                         m2 = data[0][6]
        #                         # 權力範圍
        #                         right_area = wrap_replace(data[0][7])
        #                         # 最低拍賣價格
        #                         money_down = data[0][8]
        #                 elif len(data[0]) in [11, 12]:
        #                     # 面積
        #                     m2 = data[0][8]
        #                     # 權力範圍
        #                     right_area = wrap_replace(data[0][9])
        #                     # 最低拍賣價格
        #                     money_down = data[0][10]
        #                 else:
        #                     print(
        #                         data, '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@面積 欄位長度')
        #                 # 備考
        #                 extra = None
        #                 if len(data) == 2:
        #                     extra = data[1][2]

        #                 extra = str(extra or '')
        #                 # print(extra)

        #                 #! 組資料
        #                 location = region_name + sm_original + '地號'

        #                 data_dict[location] = {
        #                     'lbkey': lb_key,
        #                     'owner': owner,
        #                     'location': location,
        #                     'location_number': None,
        #                     'door_number': None,
        #                     'details': f'{m2} {right_area} {money_down}',
        #                     'extra': extra
        #                 }
        # # 專門拿來處理建地的情況
        # elif '建' in table_list[1][1]:
        #     a = 1
        #     if a == 1:
        #         """
        #         表格欄位介紹

        #         常見: 長度8
        #         編號 ｜ 建號 ｜ 建物門牌 ｜ 主要建材層數 ｜ 樓層面積 ｜ 附屬建材用途 ｜ 權利範圍 ｜ 最低拍賣價

        #         不常見: 長度9
        #         (彰化縣)
        #         編號 ｜ 建號 ｜ 建物門牌 ｜ 主要建材層數 ｜ 樓層面積 ｜ 附屬建材用途 ｜ 權利範圍 ｜ 最低拍賣價 ｜ 保證金額
        #         """
        #         data_list = [table_list[split_num:][i:i+prepare]
        #                      for i in range(0, len(table_list[split_num:]), prepare)]
        #         for data in data_list:
        #             _, sm_key = jcBuildingSm(data[0][1])
        #             address_list = ['', '']
        #             if data[0][2]:
        #                 address_str = data[0][2]
        #                 address_list = wrap_replace(
        #                     address_str).split('--------------')

        #             # 建物座落地號 取縣市行政區段小段
        #             carName_original = address_list[0]
        #             lkeyName_re = re.compile(r'^(\D*)')
        #             lkeyName_match = lkeyName_re.match(carName_original)
        #             lkeyCarName = lkeyName_match[0]

        #             city_name = ''
        #             area_name = ''
        #             region_name = ''
        #             if '新竹市' in lkeyCarName:
        #                 lkeyCarName_list = lkeyCarName.split('　')
        #                 city_name = lkeyCarName_list[0]
        #                 area_name = lkeyCarName_list[0]
        #                 region_name = lkeyCarName_list[1]
        #             elif '嘉義市' in lkeyCarName:
        #                 lkeyCarName_list = lkeyCarName.split('區')
        #                 city_name = '嘉義市'
        #                 area_name = '嘉義市'
        #                 region_name = lkeyCarName_list[-1]
        #             else:
        #                 try:
        #                     carName_re = re.compile(
        #                         r'^(\D*?[縣市])(\D*[鄉鎮市區])?(\D*[段])?$')
        #                     carName_match = carName_re.match(lkeyCarName)
        #                     city_name = carName_match[1]
        #                     area_name = carName_match[2]
        #                     region_name = carName_match[3]
        #                 except:
        #                     logger.info(f'{lkeyCarName} 無比對到建號')
        #                     error_count += 1
        #                     continue
        #             area_name = check_area_name(city_name, area_name)
        #             if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
        #                 lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{sm_key}'

        #             else:
        #                 logger.info(
        #                     f'{city_name} {area_name} {region_name} 無比對到建號')
        #                 error_count += 1
        #                 continue

        #             address = address_list[1].replace(
        #                 ' ', '').replace('之', '-')
        #             floor = wrap_replace(data[0][4])  # 樓層面積
        #             belong = wrap_replace(data[0][5])  # 附屬
        #             right_area = wrap_replace(data[0][6])  # 權力範圍
        #             money_down = wrap_replace(data[0][7])  # 最低拍賣金額

        #             # # 備考
        #             # extra = None
        #             # if len(data) == 2:
        #             #     extra = data[1][2]
        #             # extra = str(extra or '')

        #             #! 組資料
        #             address = address.replace('台', '臺')
        #             data_dict[address] = {
        #                 'lbkey': lb_key,
        #                 'owner': owner,
        #                 'local': region_name + sm_key + '建號',
        #                 'location_number': carName_original,
        #                 'door_number': address,
        #                 'details': f'{floor}\n{belong}\n{right_area} {money_down}',
        #                 # 'extra': extra
        #             }
        #     # 為了要處理欄位中間有空格的問題因此再新增一個全新的方法, 來重新抓取欄位
        #     # elif ' 建' not in table_list[1][1] and '建  號' in table_list[5]:
        #     #     data_dict = '我就爛'
        #     # 為了要處理欄位中間沒有空格, 並且有建物門牌的問題因此再新增一個全新的方法, 來重新抓取欄位
        # else:
        #     if '地 \n \n \n目' in table_list[1]:
        #         # 這行的目的主要是為了找出,如果table_list[3]內有None的可能在排把他排除
        #         split_num = 3
        #         for num, talist in enumerate(table_list):
        #             try:
        #                 int(talist[0])
        #                 split_num = num
        #                 break
        #             except:
        #                 pass
        #         # # 判斷有沒有備考 沒的話 用1行切割
        #         prepare = 2
        #         #  print(str(table_list[split_num + 1][1])) 結果為 備考
        #         if len(table_list) > 5 and ('備' not in str(table_list[split_num + 1][1] or '')):
        #             prepare = 1
        #         # 整理可能需要的地方
        #         data_list = [table_list[split_num:][i:i+prepare]
        #                      for i in range(0, len(table_list[split_num:]), prepare)]
        #         # 這行的目的主要是為了找出,如果data內有None的可能在排把他排除
        #         data_list = list(
        #             filter(lambda x: x is not None, data_list))
        #         city_name = wrap_replace(data_list[0][0][1])
        #         area_name = wrap_replace(data_list[0][0][2])
        #         region3 = wrap_replace(data_list[0][0][3])
        #         if region3[-1] != '段':
        #             region3 += '段'
        #         region4 = wrap_replace(data_list[0][0][4])
        #         if region4 != '' and region4[-1] != '段':
        #             region4 += '小段'
        #         land_number = wrap_replace(data_list[0][0][5])
        #         if land_number[-1] != '號':
        #             land_number += '地號'
        #         word = dict(zip(map(ord, u'1234567890'),
        #                     map(ord, u'一二三四五六七八九零')))
        #         region_name = region3+region4
        #         region_name = region_name.translate(word)
        #         sm_re = re.compile(r'^(\d*)[-之]?(\d*)號?(.*)')
        #         sm_match = sm_re.match(region_name)
        #         s = sm_match[1]
        #         m = sm_match[2]
        #         location = city_name+area_name+region3+region4+land_number+'地號'
        #         if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
        #             lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{s.zfill(4)}-{m.zfill(4)}'
        #         # 面積
        #         m2 = data_list[0][0][7]
        #         right_area = data_list[0][0][8]
        #         money_down = data_list[0][0][9]
        #         extra = data_list[0][0][11]
        #         data_dict[location] = {
        #             'lbkey': lb_key,
        #             'owner': owner,
        #             'location': location,
        #             'location_number': None,
        #             'door_number': None,
        #             'details': f'{m2} {right_area} {money_down}',
        #             'extra': extra
        #         }
        #         # # =================================================================以上在處理土地,往下開始對建物動作
        #         # 計算出該pdf內編號跟附註在哪一個欄位
        #         for x in range(1, len(data_list)):
        #             data_list[x][0][0] = list(
        #                 filter(lambda x: x != None, data_list[x][0][0]))
        #             data_list[x][0][0] = list(
        #                 filter(lambda x: x != '\n', data_list[x][0][0]))
        #             data_list[x][0][0] = list(
        #                 filter(lambda x: x != ' ', data_list[x][0][0]))
        #             # # print(wrap_replace(data_list[x][0][0]))
        #             if (data_list[x][0][0]) == ['編', '號']:
        #                 start_serial_number = x
        #             if (data_list[x][0][0]) == '附註' or '備註' or ['附', '註']:
        #                 end_notes = x
        #         # # 去之後的欄位,拿到我需要的值
        #         for x in range(start_serial_number+1, end_notes):
        #             # 建號
        #             if data_list[x][0][2] != '共有部分':
        #                 # 這行的目的主要是為了找出data_list[x][0]內有None的可能在排把他排除
        #                 data_list[x][0] = list(
        #                     filter(lambda x: x is not None, data_list[x][0]))
        #                 build_number = data_list[x][0][1]
        #                 _, sm_key = jcBuildingSm(data_list[x][0][1])
        #                 # print(build_number, sm_key)
        #                 The_base_in_located = wrap_replace(
        #                     data_list[x][0][2])
        #                 address = wrap_replace(data_list[x][0][3])
        #                 address = address.replace(
        #                     ' ', '').replace('之', '-')
        #                 floor = wrap_replace(data_list[x][0][5])  # 樓層面積
        #                 right_area = wrap_replace(
        #                     data_list[x][0][6])  # 權力範圍
        #                 money_down = wrap_replace(
        #                     data_list[x][0][7])  # 最低拍賣金額
        #                 caution_money = wrap_replace(
        #                     data_list[x][0][8])  # 保證金
        #                 data_dict[build_number] = {
        #                     'lbkey': lb_key,
        #                     'owner': owner,
        #                     'local': region_name + sm_key + '建號',
        #                     'location_number': The_base_in_located,
        #                     'door_number': address,
        #                     'details': f'{floor}\n{right_area}\n{money_down} {caution_money}',
        #                 }
        #         else:
        #             # 這行的目的主要是為了找出data_list[x][0]內有None的可能在排把他排除
        #             data_list[x][0] = list(
        #                 filter(lambda x: x is not None, data_list[x][0]))
        #             build_number = data_list[x][0][1]
        #             The_base_in_located = data_list[x][0][2]
        #             floor = wrap_replace(data_list[x][0][3])  # 樓層面積
        #             right_area = wrap_replace(data_list[x][0][4])  # 權力範圍
        #             money_down = wrap_replace(data_list[x][0][5])  # 最低拍賣金額
        #             caution_money = wrap_replace(data_list[x][0][6])  # 保證金
        #             data_dict[build_number] = {
        #                 'lbkey': lb_key,
        #                 'owner': owner,
        #                 'local': region_name + sm_key + '建號',
        #                 'location_number': The_base_in_located,
        #                 'door_number': address,
        #                 'details': f'{floor}\n{right_area}\n{money_down} {caution_money}',
        #             }
        #     else:
        #         split_num = 3
        #         for num, talist in enumerate(table_list):
        #             try:
        #                 int(talist[0])
        #                 split_num = num
        #                 break
        #             except:
        #                 pass
        #         # # 判斷有沒有備考 沒的話 用1行切割
        #         prepare = 2
        #         #  print(str(table_list[split_num + 1][1])) 結果為 備考
        #         if len(table_list) > 5 and ('備' not in str(table_list[split_num + 1][1] or '')):
        #             prepare = 1
        #         # 整理可能需要的地方
        #         data_list = [table_list[split_num:][i:i+prepare]
        #                      for i in range(0, len(table_list[split_num:]), prepare)]
        #         # 這行的目的主要是為了找出,如果data內有None的可能在排把他排除
        #         data_list[0][0] = list(
        #             filter(lambda x: x is not None, data_list[0][0]))
        #         sum = 0
        #         # print(table_list)
        #         for x in range(0, len(data_list)):
        #             # 這行的目的主要是為了找出,如果data_list內有None的可能在排把他排除
        #             if data_list[x][0][0] == None:
        #                 continue
        #             if '編' in data_list[x][0][0]:
        #                 start_serial_number = x
        #             if '點' in data_list[x][0][0]:
        #                 start_serial_number = x
        #             if '備' in data_list[x][0][0]:
        #                 start_serial_number = x
        #             else:
        #                 start_serial_number = 1
        #         # print(start_serial_number)
        #         for x in range(0, start_serial_number):
        #             # 這行的目的主要是為了找出,如果data內有None的可能在排把他排除
        #             data_list[x][0] = list(
        #                 filter(lambda x: x is not None, data_list[x][0]))
        #             city_name = wrap_replace(data_list[x][0][1])
        #             area_name = wrap_replace(data_list[x][0][2])
        #             region3 = wrap_replace(data_list[x][0][3])
        #             if region3[-1] != '段':
        #                 region3 += '段'
        #             region4 = wrap_replace(data_list[x][0][4])
        #             if region4 != '' and region4[-1] != '段':
        #                 region4 += '小段'
        #             land_number = wrap_replace(data_list[x][0][5])
        #             if land_number[-1] != '號':
        #                 land_number += '地號'
        #             word = dict(zip(map(ord, u'1234567890'),
        #                         map(ord, u'一二三四五六七八九零')))
        #             region_name = region3+region4
        #             region_name = region_name.translate(word)
        #             sm_re = re.compile(r'^(\d*)[-之]?(\d*)號?(.*)')
        #             sm_match = sm_re.match(region_name)
        #             s = sm_match[1]
        #             m = sm_match[2]
        #             location = city_name+area_name+region3+region4+land_number
        #             if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
        #                 lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{s.zfill(4)}-{m.zfill(4)}'
        #             # 面積
        #             m2 = data_list[x][0][6]
        #             right_area = data_list[x][0][7]
        #             money_down = data_list[x][0][8]
        #             data_dict[location] = {
        #                 'city_name': city_name,
        #                 'area_name': area_name,
        #                 'lbkey': lb_key,
        #                 'owner': owner,
        #                 'location': location,
        #                 'location_number': None,
        #                 'door_number': None,
        #                 'details': f'{m2} {right_area} {money_down}',
        #                 'extra': None
        #             }
        #         # # =================================================================以上在處理土地,往下開始對建物動作
        #         # 計算出該pdf內編號跟附註在哪一個欄位
        #         # print(len(data_list))
        #         for x in range(0, len(data_list)+1):
        #             # print(data_list[0][x][0])
        #             # 這行的目的主要是為了找出,如果data_list內有None的可能在排把他排除
        #             # data_list[0][x][0] = list(
        #             #     filter(lambda x: x is not None, data_list[x][0][0]))
        #             if '編' in data_list[0][x][0]:
        #                 start_serial_number = x
        #             else:
        #                 start_serial_number = 0
        #             if '附' in data_list[0][x][0]:
        #                 end_notes = x
        #                 break
        #             elif '備' in data_list[0][x][0]:
        #                 end_notes = x
        #                 break
        #             elif '備\n註' in data_list[0][x][0]:
        #                 end_notes = x
        #                 break
        #             elif '共有部份' in data_list[0][x][0]:
        #                 end_notes = x
        #         # print(start_serial_number, end_notes)
        #         for x in range(start_serial_number, end_notes):
        #             if data_list[x][0][0] == [f'{end_notes}']:
        #                 try:
        #                     # 建地坐落
        #                     _, sm_key = jcBuildingSm(
        #                         data_list[x+1][0][0])
        #                     # 這行的目的主要是為了找出data_list[x+1][0]內有None的可能在排把他排除
        #                     data_list[x+1][0] = list(
        #                         filter(lambda x: x is not None, data_list[x+1][0]))
        #                     # 建號
        #                     build_number = wrap_replace(
        #                         data_list[x][0][1])
        #                     # 建物門牌
        #                     address = wrap_replace(data_list[x][0][2])
        #                     address = address.replace(
        #                         ' ', '').replace('之', '-')
        #                     The_base_in_located = wrap_replace(
        #                         data_list[x][0][3])
        #                     floor = wrap_replace(
        #                         data_list[x][0][4])  # 樓層面積
        #                     Accessory_floor = wrap_replace(
        #                         data_list[x][0][5])  # 附屬樓層
        #                     right_area = wrap_replace(
        #                         data_list[x][0][6])  # 權力範圍
        #                     money_down = wrap_replace(
        #                         data_list[x][0][7])  # 最低拍賣金額
        #                     location = city_name+area_name+region3+region4+land_number
        #                     data_dict[build_number] = {
        #                         'city_name': city_name,
        #                         'area_name': area_name,
        #                         'lbkey': lb_key,
        #                         'owner': owner,
        #                         'location': location,
        #                         'location_number': The_base_in_located,
        #                         'door_number': address,
        #                         'details': f'{floor}  {right_area}  {money_down}  {Accessory_floor}',
        #                     }
        #                 except:
        #                     _, sm_key = jcBuildingSm(
        #                         data_list[x][0][2])
        #                     build_number = wrap_replace(
        #                         data_list[x][0][1])
        #                     address = wrap_replace(data_list[x][0][3])
        #                     address = address.replace(
        #                         ' ', '').replace('之', '-')
        #                     The_base_in_located = wrap_replace(
        #                         data_list[x][0][4])
        #                     floor = wrap_replace(
        #                         data_list[x][0][5])  # 樓層面積
        #                     Accessory_floor = wrap_replace(
        #                         data_list[x][0][6])  # 附屬樓層
        #                     right_area = wrap_replace(
        #                         data_list[x][0][7])  # 權力範圍
        #                     money_down = wrap_replace(
        #                         data_list[x][0][8])  # 最低拍賣金額
        #                     location = city_name+area_name+region3+region4+land_number
        #                     data_dict[build_number] = {
        #                         'city_name': city_name,
        #                         'area_name': area_name,
        #                         'lbkey': lb_key,
        #                         'owner': owner,
        #                         'location': location,
        #                         'location_number': The_base_in_located,
        #                         'door_number': address,
        #                         'details': f'{floor} {right_area} {money_down} {Accessory_floor}',
        #                     }
        #             else:
        #                 try:
        #                     # 建地坐落
        #                     _, sm_key = jcBuildingSm(
        #                         data_list[x+1][0][0])
        #                     # 這行的目的主要是為了找出data_list[x+1][0]內有None的可能在排把他排除
        #                     data_list[x+1][0] = list(
        #                         filter(lambda x: x is not None, data_list[x+1][0]))
        #                     # 建號
        #                     build_number = wrap_replace(
        #                         data_list[x][0][1])
        #                     # 建物門牌
        #                     address = wrap_replace(data_list[x][0][2])
        #                     address = address.replace(
        #                         ' ', '').replace('之', '-')
        #                     The_base_in_located = wrap_replace(
        #                         data_list[x][0][3])
        #                     floor = wrap_replace(
        #                         data_list[x][0][4])  # 樓層面積
        #                     Accessory_floor = wrap_replace(
        #                         data_list[x][0][5])  # 附屬樓層
        #                     right_area = wrap_replace(
        #                         data_list[x][0][6])  # 權力範圍
        #                     money_down = wrap_replace(
        #                         data_list[x][0][7])  # 最低拍賣金額
        #                     location = city_name+area_name+region3+region4+land_number
        #                     data_dict[build_number] = {
        #                         'city_name': city_name,
        #                         'area_name': area_name,
        #                         'lbkey': lb_key,
        #                         'owner': owner,
        #                         'location': location,
        #                         'location_number': The_base_in_located,
        #                         'door_number': address,
        #                         'details': f'{floor}  {right_area}  {money_down}  {Accessory_floor}',
        #                     }
        #                 except:
        #                     _, sm_key = jcBuildingSm(
        #                         data_list[x][0][2])
        #                     build_number = wrap_replace(
        #                         data_list[x][0][1])
        #                     address = wrap_replace(data_list[x][0][3])
        #                     address = address.replace(
        #                         ' ', '').replace('之', '-')
        #                     The_base_in_located = wrap_replace(
        #                         data_list[x][0][4])
        #                     floor = wrap_replace(
        #                         data_list[x][0][5])  # 樓層面積
        #                     Accessory_floor = wrap_replace(
        #                         data_list[x][0][6])  # 附屬樓層
        #                     right_area = wrap_replace(
        #                         data_list[x][0][7])  # 權力範圍
        #                     money_down = wrap_replace(
        #                         data_list[x][0][8])  # 最低拍賣金額
        #                     location = city_name+area_name+region3+region4+land_number
        #                     data_dict[build_number] = {
        #                         'city_name': city_name,
        #                         'area_name': area_name,
        #                         'lbkey': lb_key,
        #                         'owner': owner,
        #                         'location': location,
        #                         'location_number': The_base_in_located,
        #                         'door_number': address,
        #                         'details': f'{floor} {right_area} {money_down} {Accessory_floor}',
        #                     }
        # return data_dict


def parserPDF_2(lists_df, code_datas):
    data_dict = {}
    for table_list in lists_df:
        try:
            owner = table_list[0][0][table_list[0][0].index('：')+1:]
        except:
            owner = table_list[0][0][table_list[0][0].index('人:')+2:]
        # 分割細項 去掉標題三行 用編號判斷起始點
        split_num = 3
        for num, talist in enumerate(table_list):
            try:
                int(talist[0])
                split_num = num
                break
            except:
                pass
            # # 判斷有沒有備考 沒的話 用1行切割
        prepare = 2
        #  print(str(table_list[split_num + 1][1])) 結果為 備考
        if len(table_list) > 5 and ('備' not in str(table_list[split_num + 1][1] or '')):
            prepare = 1
        data_list = [table_list[split_num:][i:i+prepare]
                     for i in range(0, len(table_list[split_num:]), prepare)]
        for x in range(0, len(data_list)):
            # 這行的目的主要是為了找出,如果data_list內有None的可能在排把他排除
            if data_list[x][0][0] == None:
                continue
            if '備' in data_list[x][0][0]:
                start_serial_number = x
        for x in range(0, start_serial_number):
            # 這行的目的主要是為了找出,如果data內有None的可能在排把他排除
            data_list[x][0] = list(
                filter(lambda x: x is not None, data_list[x][0]))
            city_name = wrap_replace(data_list[x][0][1])
            if city_name[-1] != '市':
                city_name += '市'
            area_name = wrap_replace(data_list[x][0][2])
            if area_name[-1] != '區':
                area_name += '區'
            region3 = wrap_replace(data_list[x][0][3])
            if region3[-1] != '段':
                region3 += '段'
            region4 = wrap_replace(data_list[x][0][4])
            if region4 != '' and region4[-1] != '段':
                region4 += '小段'
            land_number = wrap_replace(data_list[x][0][5])
            if land_number[-1] != '號':
                land_number += '地號'
            word = dict(zip(map(ord, u'1234567890'),
                        map(ord, u'一二三四五六七八九零')))
            region_name = region3+region4
            # region_name = region_name.translate(word)
            sm_re = re.compile(r'^(\d*)[-之]?(\d*)號?(.*)')
            sm_region = region3+region4+land_number
            sm_region = sm_region.translate(word)
            sm_match = sm_re.match(sm_region)
            s = sm_match[1]
            m = sm_match[2]
            if s == '':
                s = land_number[0:3]
            area_name = check_area_name(city_name, area_name)
            location = city_name+region_name + land_number
            if city_name in code_datas and area_name in code_datas[city_name] and region_name in code_datas[city_name][area_name]:
                lb_key = f'{code_datas[city_name][area_name][region_name]["all_code"]}_{s.zfill(4)}-{m.zfill(4)}'
            # 面積
            m2 = data_list[x][0][6]
            right_area = data_list[x][0][7]
            money_down = data_list[x][0][8]
            data_dict[location] = {
                'lbkey': lb_key,
                'owner': owner,
                'location': location,
                'location_number': None,
                'door_number': None,
                'details': f'{m2} {right_area} {money_down}',
                'extra': None
            }
    return data_dict


def new_PDF(lists_df, code_datas):
    error_count = 0
    data_dict = {}
    for table_list in lists_df:
        try:
            owner = table_list[0][0][table_list[0][0].index('：')+1:]
        except:
            owner = table_list[0][0][table_list[0][0].index('人:')+2:]
        # # # 分割細項 去掉標題三行 用編號判斷起始點
        split_num = 3
        for num, talist in enumerate(table_list):
            try:
                int(talist[0])
                split_num = num
                break
            except:
                pass
        # # 判斷有沒有備考 沒的話 用1行切割
        prepare = 2
        if len(table_list) > 5 and ('備' not in str(table_list[split_num + 1][1] or '')):
            prepare = 1
        # 重新整理ＰＤＦ把空格跟None 移除,方便後續的資料整理
        print(table_list)
        # for x in range(0, len(table_list)):
        #     if table_list[x][0] == '縣 \n市':
        #         # 標別
        #         mark = table_list[x+1][0]
        #         # 城市
        #         city = wrap_replace(table_list[x+1][1])
        #         # 鄉鎮區
        #         area_name = wrap_replace(table_list[x+1][2])
        #         # 小段
        #         short_paragraph = wrap_replace(table_list[x+1][3])
        #         # 地號
        #         print(table_list[x+1])


def tidy(pdf_name):
    try:
        pdf = pdfplumber.open(pdf_name)

        page_table_list = []
        for pageIndex, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            # text = page.extract_text()
            # print(text)
            for table in tables:
                # 處理被pdf分割的表格

                # 逐欄確認最後一行是否是空的 是的話刪除最後一行
                nota = False
                for ta in table[-1]:
                    if not (ta == '' or ta == None):
                        nota = True
                if nota == False:
                    table = table[:-1]

                # 處理 表格合併
                if page_table_list:
                    # 有處理完的表格
                    page_table_list[-1][0]

                    #! 處理表格異常
                    if table == []:
                        page_table_list = None
                        return page_table_list
                        raise TableException('處理表格異常')

                    if (len(page_table_list[-1][0]) == len(table[0])) and ('財產所有人' not in str(table[0][0])) and ('編' not in str(table[0][0])) and len(table) > 1 and ('編' not in str(table[1][0])):
                        # 確認 已處理表格和未處理的表格長度一致 未處理表格開頭非:財產所有人 進行表格合併
                        if table[0][0] == '' and table[0][1] != '備考':
                            # 表格第一列 第一欄為空 第一欄不為備考
                            for num in range(len(page_table_list[-1][-1])):
                                if table[0][num]:
                                    # 要合併的位置有資料
                                    if page_table_list[-1][-1][num]:
                                        page_table_list[-1][-1][num] += table[0][num]
                                    else:
                                        page_table_list[-1][-1][num] = table[0][num]
                            sa_table = table[1:]
                        else:
                            sa_table = table
                        page_table_list[-1].extend(sa_table)
                        table = page_table_list.pop()

                # 表格只有2欄 不儲存
                if len(table[0]) == 2:
                    continue
                elif len(table) == 1:
                    # 處理財產所有人被截斷
                    if '財產所有人' in table[0][0]:
                        continue

                if len(table[0]) == 3:
                    # 處理備考被截斷
                    if table[0][0] == '' and table[0][1] == '備考':
                        pacut = [None, table[0][1], table[0][2]]
                        for _ in range(len(page_table_list[-1][-1])-3):
                            pacut.append(None)
                        page_table_list[-1].append(pacut)
                    elif table[0][0] == '' and table[0][1] == '' and (page_table_list[-1][-1][1] == '備考'):
                        # 備考超過一行被截斷
                        page_table_list[-1][-1][2] += table[0][2]
                    table = page_table_list.pop()

                if "財產所有人" not in str(table[0][0]):
                    # 確認上1頁最後40行 是否有 財產所有人  有的話 owner 裡
                    pdf_text = pdf.pages[pageIndex-1].extract_text()
                    r20_line = pdf_text.splitlines()[-40:]
                    r20_line.reverse()
                    line_index = 0
                    owner = ''
                    for index, line in enumerate(r20_line):
                        if '財產所有人' in line:
                            line_index = index
                            break
                    if line_index:
                        r20_line = r20_line[1:line_index+1]
                        r20_line.reverse()
                        owner = ''.join(r20_line)

                    # 先判斷第一行格式 是否為 第一欄有資料 後面無資料
                    if owner and table[0][0] and (not (table[0][1] or table[0][2] or table[0][3])):
                        table[0][0] = owner + table[0][0]
                    else:
                        # 判斷有沒有上一個表格 有的話回塞
                        pacut = []
                        if owner and (line_index <= 5):
                            pacut = [owner]
                        elif page_table_list:
                            pacut = [page_table_list[-1][0][0]]
                        elif owner:
                            pacut = [owner]

                        if pacut:
                            for _ in range(len(table[0])-1):
                                pacut.append(None)
                            table.insert(0, pacut)  # 插入在列表第一行
                page_table_list.append(table)
    except Exception as e:
        logger.info(
            f'{str(e)} exception in line {sys.exc_info()[2].tb_lineno}')
        page_table_list = []
    return page_table_list


if __name__ == '__main__':
    # file_list = [f for f in os.listdir(
    #     folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # count = 0
    # for pdf in file_list:
    #     if pdf != '.DS_Store':
    a = 'A_1080400304911_1.pdf'
    b = 'A_1040100009137_2.pdf'
    c = '1090100012556_1_1.pdf'

    want_pdf = c
    code_datas = get_all_code(1)
    lists_df = tidy(
        f'C:\Users\88698\work\test\all_pdf\{want_pdf}')
    # try:
    # print(lists_df)
    for table_list in lists_df:
        owner = table_list[0][0].split(
            "：")[1] if "：" in table_list[0][0] else table_list[0][0].split("人:")[1].strip()
    if lists_df == []:
        print('這個裡面沒有表格')
    else:
        datas = parserPDF(lists_df, code_datas)
        print(datas)
    #     new_datas = new_PDF(lists_df, code_datas)
    #         print(datas)
    #     if not lists_df:
    #         logger.info(f'{want_pdf} 解析PDF失敗')
    #     print(f'檔名：{want_pdf}')
    #     # try:
    #         print(f'原始pdf拉出資料：{lists_df[0][3]}')
    #     except:
    #         print(f'原始pdf拉出資料：{lists_df[1][3]}')
    #     print(f'輸出結果：{datas}')
    # except:
    #     # 為了處理,pdf中間有時候會被誆誤認為表格的情況
    #     lists_df = lists_df[1:]
    #     for table in lists_df:
    #         table.pop(0)
    #         owner = table[0][0].split(
    #             "：")[1] if "：" in table[0][0] else table[0][0].split("人:")[1].strip()
    #     if lists_df == []:
    #         print('這個裡面沒有表格')
    #     else:
    #         datas = parserPDF_2(lists_df, code_datas)
    #     if not lists_df:
    #         logger.info(f'{want_pdf} 解析PDF失敗')
    #     print(f'檔名：{want_pdf}')
    #     try:
    #         print(f'原始pdf拉出資料：{lists_df[0][3]}')
    #     except:
    #         print(f'原始pdf拉出資料：{lists_df[1][3]}')
    #     print(f'輸出結果：{datas}')
