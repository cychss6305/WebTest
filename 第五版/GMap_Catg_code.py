#https://stackoverflow.com/questions/34576665/setting-proxy-to-urllib-request-python3
from bs4 import BeautifulSoup
import urllib.request
import time
import os
import socks
import socket
#import requests
from urllib.request import urlopen

def GMap_Catg(url):

    temp_str = ''
    try :
        html = urlopen(url).read().decode('utf-8')
        
    except : #改一次撈一頁，有多少拿多少，list數量=0就再撈一次
        print('被擋了' )
        #呼叫洋蔥伺服器:https://hardliver.blogspot.com/2017/06/web-crawler-tor-ip.html
        socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
        socket.socket = socks.socksocket

        return  GMap_Catg(url)
    
    soup = BeautifulSoup(html, features='lxml')
    all_href = soup.find_all('meta', {"itemprop": "description"})
    href = all_href[0]['content']
    #取得那段文字 
    if href.find('·') == -1:
        return 'NULL' 
    elif href.find('★') == -1:
        b = 0
        e = href.find(r'·')-1
        temp_str = href[b:e]
    else:
        b = href.find(r'·')+1
        e = href.find(r'·',b,len(href))
        temp_str = href[b:e]
    return temp_str

