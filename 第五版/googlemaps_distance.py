import googlemaps
import os
from key import key



def get_googlemaps_distance(query,home): # 抓車距 , 車時
    
    #global company_Ename
    Ans = []
    gmaps = googlemaps.Client(key=key) 
  
    my_dist = gmaps.distance_matrix(query,home)['rows'][0]['elements'][0]['distance']['text'] #'destination_addresses','origin_addresses','rows':車時車距,'status'
    home_Ename = gmaps.distance_matrix(query,home)['destination_addresses'][0]
    #company_Ename = gmaps.distance_matrix(query,home)['origin_addresses'][0]
    #my_time = gmaps.distance_matrix(query,home)['rows'][0]['elements'][0]['duration']['text'] #車時
    Ans.append(my_dist)
    #Ans.append(my_time)
    return Ans,home_Ename