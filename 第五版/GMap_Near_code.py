#https://jingwen-z.github.io/how-to-get-places-reviews-on-google-maps-by-place-api/
import googlemaps
import os
import pandas as pd
import numpy as np
import requests
from pandas import DataFrame 

def GMap_Near(GOOGLE_PLACES_API_KEY,x,y):
    # Client
    gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY) 
    lists=[]
    # Radar search
    #location = (22.999099, 120.219615)
    location = (x, y)
    
    radius = 1000 #公尺
    #place_type = ['餐廳','公司','學校'] # 注意語系問題
    #place_type = ['restaurant','company','school']
    
    #紀錄數量
    c = 0
    r = 0 
    s = 0
    map = [c,r,s]
    r = len(gmaps.places_nearby(location, radius,keyword='restaurant')['results'])
    c = len(gmaps.places_nearby(location, radius,keyword='company')['results']) # 最多20筆
    s = len(gmaps.places_nearby(location, radius,keyword='school')['results'])
    lists.append([r,c,s])
    #print(lists)
    return lists
def GMap_Near_rating_total(GOOGLE_PLACES_API_KEY,x,y):
    #評價平均分數
    search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    location = '{0},{1}'.format(x,y)
    key = GOOGLE_PLACES_API_KEY
    search_url = search_url+"?location={0}&rankby={1}&key={2}".format(location,'distance',key)
    search_req = requests.get(search_url)
    search_json = search_req.json()
    try:
        total = search_json['results'][0]['user_ratings_total']
    except IndexError:
        total = 'NULL'
    return total
