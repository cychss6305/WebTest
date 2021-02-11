#從proxy撈IP : https://tlyu0419.github.io/2020/02/07/WebCrawler-ProxyPool/
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import re


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options)

def proxies_list():
    
    s = 0
    ActIps = []
    # 用迴圈逐一打開分頁
    url = 'http://free-proxy.cz/zh/proxylist/country/US/https/ping/all/1' #最後的數字可以用for寫
    print('Dealing with {0}'.format(url))
    driver.get(url)
    soup = BeautifulSoup(driver.page_source)
    for j in soup.select('tbody > tr'):

        # 用正則表達式抓取IP
        if re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', str(j)):
            IP = re.findall('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', str(j))[0]
            Port = soup.select('tbody > tr > td > span')[0].string
            proxy = {'http':'http://'+ IP + ':' + Port,
           'https':'https://'+ IP + ':' + Port} 
            try:
                # 隨機找的一篇新聞即可
                url = 'https://www.chinatimes.com/realtimenews/20200205004069-260408'
                resp = requests.get(url, proxies=proxy, timeout=2)
                if str(resp.status_code) == '200':
                    ActIps.append(pd.DataFrame([{'IP':IP, 'Port':Port}]))
                    print('Succed: {}:{}'.format(IP, Port))
                    s += 1
                    if s == 5:
                        break
                else:
                    print('Failed: {}:{}'.format(IP, Port))
            except:
                    print('Failed: {}:{}'.format(IP, Port))
    
    ActIps = pd.concat(ActIps, ignore_index=True)
    return ActIps
