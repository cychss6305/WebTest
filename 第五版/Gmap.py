import googlemaps
import os

#取得地點附近type的類型店家名稱
def GMap_Site(GOOGLE_PLACES_API_KEY,x,y):
    # Client
    gmaps = googlemaps.Client(key=GOOGLE_PLACES_API_KEY) 
    lists=[]
    # Radar search
    #location = (22.999099, 120.219615)
    location = (x, y)
    
    radius = 5000 #公尺
    #place_type = ['公司','百貨','飯店','銀行','郵局'] # '類型 : '古蹟','公園' ， 注意語系問題
    place_type = ['company','department store','hotel','bank','post office']

    count = len(gmaps.places_nearby(location, radius)['results'])
    for i in range(count-1):
        for j in place_type:
            try:
                places_nearby_result = gmaps.places_nearby(location, radius,keyword=j)['results'][i]['name']
                lists.append(places_nearby_result)
            except IndexError:
                print('NotFount {0}'.format(j))
    return lists
            