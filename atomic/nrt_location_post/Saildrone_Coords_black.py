#Senya Stein
#CSCI 101 
#Section B

#!/usr/bin/env python
# coding: utf-8

#license = Apache 2.0 open source code

#Extracts date, lat, lon from Saildrone data 
#Code adapted from Chelle Gentemann, Johannes Karstensen 

#import relevant libraries and functions
import json
import requests
import time
import datetime
import numpy as np

from ipyleaflet import Map, basemaps, GeoJSON, LayersControl

#web requests using requests

wfs_base_url = "https://maps.geomar.de/geoserver/OceanEddies/wfs" #server location
requested_layer = "OceanEddies:current_positions"
#dictionary of data
requests_parameters = {
                        'service': 'wfs',
                        'version': '1.0.0',
                        'request': 'getFeature',
                        'typename': requested_layer,
                        #filter the results on the server
                        'CQL_FILTER': "type like 'WaveGlider'",  # OCG CQL filter
                        'viewparams': "maxage:48",  # parameters for custom view on geoserver: set max age of position to 48h 
                        "outputformat": "application/json"
                      }
response = requests.get(wfs_base_url, params=requests_parameters)
print(f'use the following link for your query: {response.url}')

wg_positions = GeoJSON(data=response.json(), hover_style={'fillColor': 'red'}, name='WaveGlider Positions') 
print(response.json())


#assign the web response to dict_assets (a dictionary containing all the assets)

dict_assets = response.json()
dict_assets

#assign dict values to variables 
dict_assets['features'][0]['properties']['obs_timestamp']
dict_assets['features'][0]['properties']['type']
dict_assets['features'][0]['geometry']['coordinates']
date = dict_assets['features'][0]['properties']['obs_timestamp']                          

#converts time to Unix timestamp

def convertunix(date):
    
    #we don't need the Z at the end
    date = np.datetime64(date.replace('Z', ''))

    timestamp = (date - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')
    return timestamp


#extracts latitude
def coordlat(coords):
    coords = dict_assets['features'][0]['geometry']['coordinates']
    lat = coords[0]
    return lat
    
#extracts longitude
def coordlon(coords):
    coords = dict_assets['features'][0]['geometry']['coordinates']
    lon = coords[1]
    return lon   

#finds number of assets to extract
number_of_assets = len(dict_assets['features'])
print('Asset Number = ' + str(number_of_assets))

asset_dictionary = {} #this will store the final lat lon and time


i = 0

#adds each asset to dictionary to output
while i < number_of_assets:

    timestamp = convertunix(dict_assets['features'][i]['properties']['obs_timestamp']) #timestamp
    aplatform_id = dict_assets['features'][i]['properties']['platform_id'] #platform id
    atype = dict_assets['features'][i]['properties']['type'] #platform type
    rlat = coordlon(dict_assets['features'][i]['geometry']['coordinates']) #latitude
    rlon = coordlon(dict_assets['features'][i]['geometry']['coordinates']) #longitude
    
    
    
    #final dictionary of all relevant information (frome above)
    asset_dictionary[i] = { 
      "type" : atype,
      "mmsi" : aplatform_id,
      "latitude" : rlat,
      "longitude" : rlon,
      "timestamp" : np.int(timestamp) 
      }
    print(asset_dictionary[i])
    i+=1
