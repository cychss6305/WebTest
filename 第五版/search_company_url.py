#負責套公式算兩地點距離
#-*- coding: utf-8 -*-
import requests
import pandas as pd
import numpy as np
import os
import googlemaps 
import math

from pandas import DataFrame 
from key import key
from flask import Flask, request, url_for, send_from_directory,send_file,render_template,jsonify

app = Flask(__name__)

search_name_url = "https://maps.googleapis.com/maps/api/place/textsearch/json" #name搜尋
details_url = "https://maps.googleapis.com/maps/api/place/details/json?language=zh-TW" #爬下來是中文

EARTH_REDIUS = 6378.137

def rad(d):
    return d * math.pi / 180.0

def getDistance(lat1, lng1, lat2, lng2):
    radLat1 = rad(lat1)
    radLat2 = rad(lat2)
    a = radLat1 - radLat2
    b = rad(lng1) - rad(lng2)
    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a/2), 2) + math.cos(radLat1) * math.cos(radLat2) * math.pow(math.sin(b/2), 2)))
    s = s * EARTH_REDIUS
    return s

def result_url(home,company): #查看看公司地點案排序在算距離

   # dis_list = {'place_id':[],'home_lat':[],'home_lng':[],'dist':[]}
    dis_list = {'place_id':[],'dist':[]}
    #home = '台南市新營區開元路61之17號5樓'
    query = home[0:3]+company #以住家地址的縣市找公司 ， 所以未考慮跨縣市工作的對象 ex:ABC8466DEF_1可能是
    
    search_payload = {"key":key, "query":query}
    search_req = requests.get(search_name_url, params=search_payload)
    search_company_json = search_req.json()

    search_payload = {"key":key, "query":home}
    search_req = requests.get(search_name_url, params=search_payload)
    search_home_json = search_req.json()
    
    
    if search_company_json['status'] == 'OK' and search_home_json ['status'] == 'OK':
        count = len(search_company_json['results'])
        '''
        if count > 5: #就找5筆
            count = 5
        '''
        if count > 1: #就空值
            dis_df = pd.DataFrame(dis_list)
            return dis_df
        for i in range(count):
            #兩地點經緯度
            company_lat = search_company_json['results'][i]["geometry"]["location"]["lat"] 
            company_lng = search_company_json['results'][i]["geometry"]["location"]["lng"]
            home_lat = search_home_json['results'][0]["geometry"]["location"]["lat"] 
            home_lng = search_home_json['results'][0]["geometry"]["location"]["lng"]
            
            dis_list['place_id'].append(search_company_json['results'][i]['place_id'] )
            #dis_list['home_lat'].append(home_lat )
            #dis_list['home_lng'].append(home_lng )
            dis_list['dist'].append(getDistance(company_lat,company_lng,home_lat,home_lng) )#算距離
                  
        dis_df = pd.DataFrame(dis_list)
        '''
        dis_df = dis_df.sort_values(by=['dist'],ascending=[True]) #假如需要看全部的公司離住家最近的距離5筆的話，count拿掉並把註解拿掉
        dis_df.reset_index(inplace=True,drop=True)
        
        if dis_df.shape[0] >= 5:
            dis_df = dis_df[dis_df['dist']<100].iloc[0:5,:]
        else:
        '''
        dis_df = dis_df[dis_df['dist']<100].iloc[0:dis_df.shape[0],:] #選100km內的
        return dis_df
    else:
        dis_df = pd.DataFrame(dis_list)
        return dis_df



    
    
'''

''' 

    
    
