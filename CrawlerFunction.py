import requests
from bs4 import BeautifulSoup
import jieba
#import monpa
import json
import datetime
import re
import urllib
import time
import random
import os,sys
from googleapiclient.discovery import build

#讀入負面字詞.txt
f = open('negative.txt',encoding='utf-8-sig')
string=f.read()
negative=string.strip().split("\n")
f.close()
        
NGWords=["、","。","，",",","?",".","!"," "," ",":","-",";",")","(","...","的","公司","有限",'股份有限公司',
                 '股份','1','2','3','4','5','6','7','8','9','0','．','/',', ','（','）','·',' · ',' ·',">","<","；",
                 "：",'|','！',"『","』","---","僅","供","必","是","也","@","【","】","\n"," "]


def Catch():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    
    #錯誤類型、詳細錯誤訊息、出現錯誤的檔案、錯誤的行號，這些資訊寫進一個字串
    Message=str(exc_type)+" "+str(exc_obj)+" "+str(fname)+" "+str(exc_tb.tb_lineno)+"\n"
    return Message

def Search(Input):
        #headers為了設定成電腦版格式的網頁
        headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        Result=[]
        
        #爬取網頁
        time.sleep(random.randint(5,15))
        url = "https://www.google.com.tw/search?q=" + Input + "&start=0"+"&num=20"
        response = requests.get(url,headers=headers,timeout=30)#Input為搜尋網址，timeout為爬取時等待時間
        input_html = response.text
        soup = BeautifulSoup(input_html,"html.parser")
        #偵測被擋
        if str(soup).find("Our systems have detected unusual traffic from your computer network.")!=-1:
            print(re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', str(soup))[0],"被擋")
            Result="被擋"
        else:
            # <div class="g"> 這個html tag包含標題、內文、網址
            #findAll出整個soup的這種tag，存成list
            result=soup.findAll("div", {"class": "g"})
            
            #從list整理成所需格式
            for i in result:
                #title的html tag為<h3 class="LC20lb DKV0Md">
                #content的html tag為<span class="aCOpRe">
                #根據有沒有title來取捨
                if i.find("h3",{"class":"LC20lb DKV0Md"})!=None:
                    title=i.find("h3",{"class":"LC20lb DKV0Md"}).text.replace(u'\xa0', u' ')
                    url=i.find("a", {"class": None}, href=True)["href"]
                    content=i.find("span",{"class":"aCOpRe"}).text.replace(u'\xa0', u' ')
                    Result.append({"Title":title,"Content":content,"Url":url})
        return Result

def GoogleSearchAPI(Input):
    Result=[]
    API_KEY = "AIzaSyBBdFe3rT7yhw_Asljzt2TfvRF26mIkPPo"#key
    SEARCH_ENGINE_ID = "b4420004900dab832"#search engine id
    service = build("customsearch", "v1", developerKey=API_KEY)
    res = service.cse().list(q=Input, cx=SEARCH_ENGINE_ID).execute()
    try:
        search_items = res.get("items")
        if search_items!=None:#如果搜尋結果不為空
            for i in search_items:
                title=i.get("title").replace("\n","",10).replace("\xa0","",10)
                content=i.get("snippet").replace("\n","",10).replace("\xa0","",10)
                url=i.get("link").replace("\n","",10).replace("\xa0","",10).replace("more-tel/","")
                Result.append({"Title":title,"Content":content,"Url":url})
        else:
            Result=[]
    except:
        Result=Catch()
    return Result
    
def Craw(Input,way):
    #try catch一次
    try:
        if way==0:
            Data=Search(Input)
        else:
            Data=GoogleSearchAPI(Input)
    except:
        try:
            if way==0:
                Data=Search(Input)
            else:
                Data=GoogleSearchAPI(Input)
        except Exception as e:
            Data=Catch()
    return Data

def APICut(Words,WordsDict,InputName):#要斷詞的字串、斷詞套件、斷詞後的存放地方、InputName為了跳脫出現在InputName的字詞

    CutWords=jieba.cut(Words)
        
    for word in CutWords:
        if word not in NGWords and InputName.find(word)==-1:#跳過NGWord、出現在InputName的字詞
            if WordsDict.get(word)==None:#在WordList沒有的話，則新增
                WordsDict.update({word:1})
            else:#在WordList有的話，則次數+1
                WordsDict[word]+=1
    return WordsDict

def SearchYP(YPUrl):#黃頁網址
    def Do():
        
        #爬取黃頁的整個網頁
        YPresponse = requests.get(YPUrl)
        YPresponse.encoding = 'UTF-8-sig'
        YPinput_html = YPresponse.text
        YPsoup = BeautifulSoup(YPinput_html,"html.parser")
        
        #根據html tag找到店家類型
        YPSearchResult = YPsoup.findAll("div", {"class":"inner"})
        if YPSearchResult[0].find("li").text[0]!="\n":
            Type=YPSearchResult[0].find("li").text
        else:
            Type="沒有搜尋到公司類型"
        return Type
    
    #try、catch一次
    try:
        Type=Do()
    except:
        try:
            Type=Do()
        except Exception as e:
            Type=Catch()
    return Type

def Dict2MaxList(CuttedWord):#存放斷詞後結果的Dictionary
    MaxList=[]
    for i in CuttedWord:
        MaxList.append([CuttedWord[i],i])
    MaxList=sorted(MaxList)#sort
    return MaxList[::-1][:10]#回傳前10個

def FillNan(Input):
    if Input==None or Input=="nan" or Input=="NaN" or Input=="Nan" or Input=="None":
        Input=""
    return Input

def ClearTele(Tele):
    Tele=FillNan(Tele)
    ClearTele=""
    passw=["1","2","3","4","5","6","7","8","9","0"]
    for i in Tele:
        if i in passw:
            ClearTele+=i
    return ClearTele

def ClearAddr(Addr):
    Addr=FillNan(Addr)
    Addr=Addr.replace("臺","台",len(Addr))
    return Addr[:2]

def ProcessInput(InputTele,InputName):
    if InputTele!="":
        Search="'"+InputTele+"'"+" site:www.iyp.com.tw/" #搜尋字，為公司電話+黃頁網址
        BackInput="'"+InputName+"'"+" site:www.iyp.com.tw/"
    else:
        Search="'"+InputName+"'"+" site:www.iyp.com.tw/" #搜尋字，為公司名稱+黃頁網址
        BackInput="'"+InputTele+"'"+" site:www.iyp.com.tw/"
    return Search,BackInput
