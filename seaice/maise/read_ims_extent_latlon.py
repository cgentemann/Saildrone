# -*- coding: utf-8 -*-
"""
Created on Mon May 22 15:36:00 2017

@author: SA01PH
"""
import numpy as np
#import matplotlib.pyplot as plt

#nx = 6144
#ny = 6144

#file_lat = tools_path + 'imslat_4km.bin'
#file_lon = tools_path + 'imslon_4km.bin'

#with open(file_lat, 'rb') as f_lat:
#    data = np.fromfile(f_lat, dtype='<f', count=nx*ny)
#    lat = np.reshape(data, [nx, ny], order='F')

#with open(file_lon, 'rb') as f_lon:
#    data = np.fromfile(f_lon, dtype='<f', count=nx*ny)
#    lon = np.reshape(data, [nx, ny], order='F')
    
#plt.plot(lon,lat)
#plt.show()

def read_ims_extent_latlon(tools_path):

    nx = 6144
    ny = 6144

    file_lat = tools_path + 'imslat_4km.bin'
    file_lon = tools_path + 'imslon_4km.bin'

    with open(file_lat, 'rb') as f_lat:
        data = np.fromfile(f_lat, dtype='<f', count=nx*ny)
        lat = np.reshape(data, [nx, ny], order='F')

    with open(file_lon, 'rb') as f_lon:
        data = np.fromfile(f_lon, dtype='<f', count=nx*ny)
        lon = np.reshape(data, [nx, ny], order='F')

    return lat, lon
