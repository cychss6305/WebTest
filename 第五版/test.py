#https://developers.google.com/places/web-service/intro
#-*- coding: utf-8 -*-
import requests
import pandas as pd
import numpy as np
import json
import os
import googlemaps 
import time
import sys
import traceback
import test

from search_company_url import result_url
from pandas import DataFrame 
from key import key
from flask import Flask, request, url_for, send_from_directory,send_file,render_template,jsonify
from  rmfile import clear_json
from GMap_Near_code import GMap_Near,GMap_Near_rating_total
from GMap_Catg_code import GMap_Catg

app = Flask(__name__)

file_site ='./'#下載路徑
json_name = "result.json" #array->orient = index
html_name = 'layout.html'
home_Ename = ''
#company_Ename = ''
errMsg = ''
search_name_url = "https://maps.googleapis.com/maps/api/place/textsearch/json" #name搜尋
search_phone_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=phonenumber"#phonenumber搜尋
details_url = "https://maps.googleapis.com/maps/api/place/details/json?language=zh-TW" #爬下來是中文


def get_url(search_url,query,id):
    try: #錯誤訊息 : https://dotblogs.com.tw/caubekimo/2018/09/17/145733
        
        url = 'NULL'
        home_name = request_home
        if home_name.find('號'): #通常號之後是幾樓，在搜尋會有問題故"號"之後拿掉
            home_name = home_name[:home_name.find('號')+1]
        else:
            home_name = home_name
        
        ##################################################################################API1 : 拿place_id 
        tStart = time.time()#計時開始
        if id == 'getphone': 
            search_phone_payload = {"key":key, "input":query}
            search_req = requests.get(search_url, params=search_phone_payload)
            search_json = search_req.json()
            
            try :
                place_id = [ search_json['candidates'][0]["place_id"] ] #抓到搜尋名稱，在results裡的place_id值裡

            except IndexError:
                return url
            
        else: #公司名稱籠統或差距大，需做距離住家100km內最近的5筆
            temp_place_id_df = result_url(home_name,query)
            
            if temp_place_id_df.empty != True:
                place_id = temp_place_id_df.values
            else: #找不到
                return url
        tEnd = time.time()
        print("It API1 cost %f sec" % (tEnd - tStart))
        #################################################################################
        
        url_list = []
        phone_list = []
        phonecheck_list = []
        GMap_Site_list = []
        GMap_Add_list = []
        GMap_Catg_list = []
        GMap_Distance_list = []
        GMap_Score_list = []
       
        for i in place_id: #1 、 5 筆
            ##################################################################################API2 : 每一筆place_id找details中的資料，url、phone、types、address
            tStart = time.time()#計時開始
            details_payload = {"key":key, "placeid":i}
            details_resp = requests.get(details_url, params=details_payload)
            details_json = details_resp.json()
            url = details_json["result"]["url"] +'&hl=zh_tw' #轉為中文Google查詢
            company_name = details_json["result"]["name"]
            tEnd = time.time()
            print("It API2 cost %f sec" % (tEnd - tStart))
            #################################################################################
            #print(url)
            if url != '': #Gmap有找到這家公司的url
                try: #Gmap有找到這家公司的電話
                    phone = (details_json["result"]["formatted_phone_number"]).replace(" ", "") #有可能Gmap沒有
                    phonecheck = 1
                except KeyError: #Gmap沒有找到這家公司的電話
                    phone = 'NULL'
                    phonecheck = 0
                
                url_list.append(url)
                phone_list.append(phone)
                phonecheck_list.append(phonecheck)
                GMap_Site_list.append(company_name)
                GMap_Add_list.append(details_json["result"]["formatted_address"])
                ##################################################################################API3 : 模擬手動查詢爬尋地類型，會被擋
                tStart = time.time()#計時開始
                GMap_Catg_list.append(GMap_Catg(url)) 
                tEnd = time.time()
                print("It API3 cost %f sec" % (tEnd - tStart))
                ##################################################################################API4 : 車距、車時
                tStart = time.time()#計時開始
                temp_dist_time = get_googlemaps_distance(details_json["result"]["formatted_address"],home_name) 
                tEnd = time.time()
                print("It API4 cost %f sec" % (tEnd - tStart))
                #################################################################################
                GMap_Distance_list.append(temp_dist_time[0]) #0:距離
                try:
                    rating = details_json["result"]["rating"]
                    total = GMap_Near_rating_total(key,details_json["result"]["geometry"]["location"]["lat"],details_json["result"]["geometry"]["location"]["lng"])
                    GMap_Score_list.append('{0}/{1}'.format(rating,total))
                            
                except KeyError:
                    GMap_Score_list.append('NULL')
    
        if len(url_list) > 0 : #放x_list資料        
            map_json['GMap_URL'].append(url_list)
            map_json['GMap_Tel_Check'].append(phonecheck_list)
            map_json['GMap_Tel'].append(phone_list)
            
            map_json['GMap_Site'].append(GMap_Site_list)
            map_json['GMap_Add'].append(GMap_Add_list)
            map_json['GMap_Catg'].append(GMap_Catg_list)
            map_json['GMap_Distance'].append(GMap_Distance_list)
            map_json['GMap_Score'].append(GMap_Score_list)
            #################################################################################API5 : 雷達查詢，住家附近地標
            tStart = time.time()#計時開始
            search_payload = {"key":key, "query":home_Ename}
            search_req = requests.get(search_name_url, params=search_payload)
            search_home_json = search_req.json()
            if search_home_json['status'] == 'OK':
                temp_near = GMap_Near(key,search_home_json['results'][0]["geometry"]["location"]["lat"] ,search_home_json['results'][0]["geometry"]["location"]["lng"]) 
                tEnd = time.time()
                print("It API5 cost %f sec" % (tEnd - tStart))
                #################################################################################
                #map_json['GMap_Near'].append(temp_near[:-1]) #地標類
                map_json['GMap_Near_Eat'].append(temp_near[0][0])#['餐廳','公司','學校']的數量
                map_json['GMap_Nearr_Comp'].append(temp_near[0][1])
                map_json['GMap_Near_Edu'].append(temp_near[0][2])
            else:
                #map_json['GMap_Near'].append('NULL') #地標類
                map_json['GMap_Near_Eat'].append('NULL')#['餐廳','公司','學校']的數量
                map_json['GMap_Nearr_Comp'].append('NULL')
                map_json['GMap_Near_Edu'].append('NULL')
            
            map_json['Status'].append('success')
            result = pd.DataFrame(map_json)
    
            #json_name = "result.json" #array->orient = index
            json = result.to_json(json_name,orient='records',force_ascii=False,lines=True)#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_json.html?highlight=to_json
            
            return url
        else: 
            url = 'NULL'
            return url
    except Exception as e:
    #   print(e)
        error_class = e.__class__.__name__ #取得錯誤類型
        detail = e.args[0] #取得詳細內容
        cl, exc, tb = sys.exc_info() #取得Call Stack
        lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
        fileName = lastCallStack[0] #取得發生的檔案名稱
        lineNum = lastCallStack[1] #取得發生的行號
        funcName = lastCallStack[2] #取得發生的函數名稱
        errMsg = "ERROR!! File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
        input_error(errMsg)
        result = pd.DataFrame(map_json)
        json = result.to_json(json_name,orient='records',force_ascii=False,lines=True)
        url = 'ERROR'
        return url

def get_googlemaps_distance(query,home): # 抓車距 , 車時
    global home_Ename #用英文名稱找會更好，不易出錯
    #global company_Ename
    Ans = []
    gmaps = googlemaps.Client(key=key) 
  
    my_dist = gmaps.distance_matrix(query,home)['rows'][0]['elements'][0]['distance']['text'] #'destination_addresses','origin_addresses','rows':車時車距,'status'
    home_Ename = gmaps.distance_matrix(query,home)['destination_addresses'][0]
    #company_Ename = gmaps.distance_matrix(query,home)['origin_addresses'][0]
    #my_time = gmaps.distance_matrix(query,home)['rows'][0]['elements'][0]['duration']['text'] #車時
    Ans.append(my_dist)
    #Ans.append(my_time)
    return Ans

def input_null():
    for i in map_json.keys():
        if i != 'App_Case_No' and i != 'Comp_Nme' and i != 'Comp_Tel':
            map_json[i].append("NULL")
def input_error(error):
    for i in map_json.keys():
        if i != 'App_Case_No' and i != 'Status' and i != 'Comp_Nme' and i != 'Comp_Tel':
            map_json[i].append("ERROR")
        if i == 'Status':
            map_json[i].append(error)
            
@app.route('/<filename>')
def download(filename): #檔案下載
    fname = filename
    return send_from_directory(file_site, fname, mimetype='application/octet-stream') #執行檔案下載

@app.route("/")
def retreive():
    return render_template(html_name)

@app.route('/',methods=['GET','POST'])
def result_dict():
    global map_json,request_number,request_search_phone,request_company,request_home,errMsg
    
    request_number = request.values['App_Case_No']
    request_search_phone = request.values['Comp_Tel']
    request_company = request.values['query']
    request_home = request.values['home']
    
    
    map_json =  {'Status':[],'App_Case_No':[],'Comp_Tel':[],
             'Comp_Nme':[],'GMap_Tel_Check':[],'GMap_URL':[],
             'GMap_Site':[],'GMap_Add':[],'GMap_Tel':[],
             'GMap_Catg':[],'GMap_Distance':[],"GMap_Score":[],
             'GMap_Near_Eat':[],'GMap_Nearr_Comp':[],'GMap_Near_Edu':[]} 
    if request.method =='POST':  
        
        tStart1 = time.time()
        if request.values['search']=='search' and request_company !='' and request_home!='' and request_number !='':
            clear_json() 
            
            map_json['App_Case_No'].append(request_number)
            map_json['Comp_Nme'].append(request_company)
            
            if request_search_phone =='' or request_search_phone[1] == '9': #沒有電話 或 是用手機號碼
                if request_search_phone =='':
                    map_json['Comp_Tel'].append('NULL')
                else:
                    map_json['Comp_Tel'].append(request_search_phone)
                url = get_url(search_name_url,request_company,'nophone')
                
                #print(map_json)
                if url != 'NULL' and url != 'N' : #有用公司地址找到
                    tEnd = time.time()
                    print("It total cost %f sec" % (tEnd - tStart1))
                    return render_template(html_name,
                                       url = map_json['GMap_URL'],
                                       query=request_company,
                                       App_Case_No = request_number,
                                       Comp_Tel = request_search_phone,
                                       home=request_home,
                                       dict_name = map_json,
                                       json=json_name)
                elif url == 'ERROR':  
                   return render_template(html_name,
                                           url = 'NULL',
                                           query=request_company,
                                           App_Case_No = request_number,
                                           Comp_Tel = request_search_phone,
                                           home=request_home,
                                           dict_name = map_json,
                                           json=json_name)
                else:#有用公司地址卻沒找到
                    input_null()
                    tEnd = time.time()
                    print("It total cost %f sec" % (tEnd - tStart1))
                    return render_template(html_name,
                                       url = 'NULL',
                                       query=request_company,
                                       App_Case_No = request_number,
                                       Comp_Tel = request_search_phone,
                                       home=request_home,
                                       dict_name = map_json,
                                       json=json_name)
            else:   #有電話 
                phone = '+886'+request_search_phone[1:] 
                map_json['Comp_Tel'].append(request_search_phone)
                url = get_url(search_phone_url,phone,'getphone')
                if url != 'NULL' and url != 'N'  : #有用公司電話找到
                    tEnd = time.time()
                    print("It total cost %f sec" % (tEnd - tStart1))
                    return render_template(html_name,
                                       url = url,
                                       query=request_company,
                                       App_Case_No = request_number,
                                       Comp_Tel = request_search_phone,
                                       home=request_home,
                                       dict_name = map_json,
                                       json=json_name)
                else : #電話找不到，改用名稱找
                    url = get_url(search_name_url,request_company,'nophone')
                    if url != 'NULL' and url != 'N' : #有用公司地址找到
                        tEnd = time.time()
                        print("It total cost %f sec" % (tEnd - tStart1))
                        return render_template(html_name,
                                           url = map_json['GMap_URL'],
                                           query=request_company,
                                           App_Case_No = request_number,
                                           Comp_Tel = request_search_phone,
                                           home=request_home,
                                           dict_name = map_json,
                                           json=json_name)
                    elif url == 'ERROR':  
                        return render_template(html_name,
                                           url = 'NULL',
                                           query=request_company,
                                           App_Case_No = request_number,
                                           Comp_Tel = request_search_phone,
                                           home=request_home,
                                           dict_name = map_json,
                                           json=json_name)
                        
                    else:#有用公司地址卻沒找到
                        input_null()
                        tEnd = time.time()
                        print("It total cost %f sec" % (tEnd - tStart1))
                        return render_template(html_name,
                                           url = 'NULL',
                                           query=request_company,
                                           App_Case_No = request_number,
                                           Comp_Tel = request_search_phone,
                                           home=request_home,
                                           dict_name = map_json,
                                           json=json_name)
        else:
            tEnd = time.time()
            print("It total cost %f sec" % (tEnd - tStart1))
            return render_template(html_name)

    

if __name__ ==  "__main__":
    app.run(host="0.0.0.0",port=8050) #http://140.116.51.164/
