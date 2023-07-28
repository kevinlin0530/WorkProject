import requests as req
import json
import pandas as pd
import argparse


class CityAreaRegionComparisonMgr():
    def __init__(self):
        super(CityAreaRegionComparisonMgr, self).__init__()
        self.city_ram = dict()
        self.area_ram = dict()
        self.region_ram = dict()
        self.url = 'http://land-data.yeshome.net.tw/'
        self.cityUrl = self.url+'bigdata/get_city/'
        self.areaUrl = self.url+'bigdata/get_area/'
        self.regionUrl = self.url+'bigdata/get_region/'

    def getCityName(self, c):
        cityName = self.city_ram.get(c)
        if cityName:
            return cityName
        else:
            res = req.post(self.cityUrl)
            json_res = json.loads(res.text)
            self.city_ram = json_res
            cityName = self.city_ram.get(c)
            return cityName

    def getAreaName(self, c_a):
        areas = self.area_ram.get(c_a[0])
        areaName = None
        if areas:
            areaName = areas.get(c_a)
        else:
            data = {
                'city_id': c_a[0]
            }
            res = req.post(self.areaUrl, data=data)
            json_res = json.loads(res.text)
            if json_res:
                self.area_ram[c_a[0]] = json_res
                areaName = json_res.get(c_a)
        return areaName

    def getRegionName(self, c_a_r):
        regions = self.region_ram.get(c_a_r[:4])
        regionName = None
        if regions:
            regionName = regions.get(c_a_r)
        else:
            data = {
                'area_id': c_a_r[:4]
            }
            res = req.post(self.regionUrl, data=data)
            json_res = json.loads(res.text)
            if json_res:
                self.region_ram[c_a_r[:4]] = json_res
                regionName = json_res.get(c_a_r)
                regionName
        return regionName

    def getCarCode(self, cityName, areaName, regionName):
        
        city = area = region = None
        for _ in range(2):
            city = self.get_key(self.city_ram, cityName)
            if city:
                break
            self.getCityName('A')
            
        if city:
            for _ in range(2):
                areas = self.area_ram.get(city)
                if areas:
                    area = self.get_key(areas, areaName)
                if area:
                    area = area.split('_')[-1]
                    break
                self.getAreaName('{}_01'.format(city))
        if area:
            for _ in range(2):
                regions = self.region_ram.get('{}_{}'.format(city, area))
                if regions:
                    region = self.get_key(regions, regionName)

                if region:
                    region = region.split('_')[-1]
                    break
                self.getRegionName('{}_{}_0001'.format(city, area))

        return city, area, region

    def get_key(self, dic, value):
        keys = [k for k, v in dic.items() if v == value]
        key = None
        if keys:
            key = keys[0]
        return key

carObj = CityAreaRegionComparisonMgr()

parser = argparse.ArgumentParser(description='Process file name.')
parser.add_argument('-name', type=str, help='File name.')
args = parser.parse_args()

name = args.name
filename = f"C:/Users/88698/Desktop/義鼎資料/{name}"
sheetname = filename.split('/')[-1]

df = pd.read_excel('{}.xlsx'.format(filename), sheet_name='{}'.format(sheetname), header=2)
df = df.drop(columns=['備註'])

df = df.fillna('')
df.dropna(axis=0,how='any')
df['地段'] = df['地段'].replace('段 ','')

def setkey(r):
    try:
        city, area, ragion = carObj.getCarCode(r['縣市'].replace('台', '臺'), r['行政區'], r['地段'])
        ms = "{}_{}_{}_{}-{}".format(city, area, ragion, str(int(r['地號母號'])).zfill(4), str(int(r['地號子號'])).zfill(4))

        return ms
    except:
        pass
    return ''

df['lbkey'] = df.apply(setkey, axis=1)

df = df[df['lbkey']!='']

df2 = pd.DataFrame(df['lbkey'], columns=['lbkey'])
df2.to_csv(f'{filename}.csv',index=False)
res = df['lbkey'].tolist()
print(res)

# url = 'https://lbor.yeshome.net.tw/tasks/create/transcript/v2/'

# def test_api(url):
#     data = {
#     'token':'399bda52-b0a9-4e59-ace6-29c088b6fd50',
#     'lbkeys': ','.join(res),
#     'priority':96,
#     'system':2,
#     'source':f"KEVIN 義鼎任務"
#     }
#     response = req.post(url,data=data)
#     print(response.status_code)

# test_api(url)