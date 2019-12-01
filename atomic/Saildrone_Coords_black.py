#!/usr/bin/env python
# coding: utf-8

#name
#date
#license = Apache 2.0 open source code

#  Description of program's purpose
# What code you got from others, what you wrote yourself  (eg. say adapted from .... & give credit to Johannes)
#

import json
import requests
import time
import datetime
import numpy as np

from ipyleaflet import Map, basemaps, GeoJSON, LayersControl

# web requests using requests

wfs_base_url = "https://maps.geomar.de/geoserver/OceanEddies/wfs"  # server location
requested_layer = "OceanEddies:current_positions"
# dictionary of data
requests_parameters = {
    "service": "wfs",
    "version": "1.0.0",
    "request": "getFeature",
    "typename": requested_layer,
    # filter the results on the server
    "CQL_FILTER": "type like 'WaveGlider'",  # OCG CQL filter
    "viewparams": "maxage:48",  # parameters for custom view on geoserver: set max age of position to 48h
    "outputformat": "application/json",
}
response = requests.get(wfs_base_url, params=requests_parameters)
print(f"use the following link for your query: {response.url}")

wg_positions = GeoJSON(
    data=response.json(), hover_style={"fillColor": "red"}, name="WaveGlider Positions"
)
print(response.json())


# assign the web response to dict_assets (a dictionary containing all the assets)

dict_assets = response.json()
dict_assets

dict_assets["features"][0]["properties"]["obs_timestamp"]
dict_assets["features"][0]["properties"]["type"]
dict_assets["features"][0]["geometry"]["coordinates"]
date = dict_assets["features"][0]["properties"]["obs_timestamp"]

# converts time to Unix timestamp


def convertunix(date):

    date = np.datetime64(date.replace("Z", ""))

    timestamp = (date - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(1, "s")
    return timestamp


def coordlat(coords):
    coords = dict_assets["features"][0]["geometry"]["coordinates"]
    lat = coords[0]
    return lat


def coordlon(coords):
    coords = dict_assets["features"][0]["geometry"]["coordinates"]
    lon = coords[1]
    return lon


length = len(dict_assets["features"])
asset_dictionary = {}
print("length = " + str(length))

i = 0
while i < length:

    timestamp = convertunix(dict_assets["features"][i]["properties"]["obs_timestamp"])
    aplatform_id = dict_assets["features"][i]["properties"]["platform_id"]
    atype = dict_assets["features"][i]["properties"]["type"]
    rlat = coordlon(dict_assets["features"][i]["geometry"]["coordinates"])
    rlon = coordlon(dict_assets["features"][i]["geometry"]["coordinates"])

    # final dictionary of all relevant information
    asset_dictionary[i] = {
        "type": atype,
        "mmsi": aplatform_id,
        "latitude": rlat,
        "longitude": rlon,
        "timestamp": np.int(timestamp),
    }
    print(asset_dictionary[i])
    i += 1
