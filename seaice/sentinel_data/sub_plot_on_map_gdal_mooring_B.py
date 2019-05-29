# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 15:04:52 2017

@author: SA01PH
"""

from mpl_toolkits.basemap import Basemap
import osr, gdal
import matplotlib.pyplot as plt
import numpy as np
from pyproj import Proj


def sub_plot_on_map_gdal(path, file,lon_mooring,lat_mooring):

    print(path+file+'.tif')
    ds = gdal.Open(path + file +".tif")

    data = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    project = ds.GetProjection()
    
    data[data==0]=100.

    xres = gt[1]
    yres = gt[5]

    # get the edge coordinates and add half the resolution 
    # to go to center coordinates
    xmin = gt[0] + xres * 0.5
    xmax = gt[0] + (xres * ds.RasterXSize) - xres * 0.5
    ymin = gt[3] + (yres * ds.RasterYSize) + yres * 0.5
    ymax = gt[3] - yres * 0.5

    ds = None

    # create a grid of xy coordinates in the original projection
    xy_source = np.mgrid[xmin:xmax+xres:xres, ymax+yres:ymin:yres]

    # Create the figure and basemap object
    fig = plt.figure(figsize=(12, 6))
    m = Basemap(projection='tmerc', lat_0=lat_mooring, lon_0=lon_mooring, llcrnrlon=25., \
                llcrnrlat=80.,urcrnrlon=35.,urcrnrlat=82.5, resolution='f')

    # Create the projection objects for the convertion
    # original (Albers)
    #inproj = osr.SpatialReference()
    #inproj.ImportFromWkt(project)
    #inproj.ImportFromProj4(proj)

    # Get the target projection from the basemap object
    #outproj = osr.SpatialReference()
    #outproj.ImportFromProj4(m.proj4string)

    # Convert from source projection to basemap projection
    #xx, yy = pyproj.transform(inproj, outproj)
    #xx, yy = convertXY(xy_source, inproj, outproj)

    #convert utm coordinates into lat/lon
    myProj = Proj("+proj=utm +zone=36, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    lons, lats = myProj(xy_source[0,:,:], xy_source[1,:,:], inverse=True)
    #lons, lats = np.meshgrid(lons,lats)
    xx, yy = m(lons,lats)

    #set sigma0 limit in db
    db_min = -30
    db_max = -10
    sigma0_min = 10.**(db_min*0.1)
    sigma0_max = 10.**(db_max*0.1)


    # plot the data (first layer)
    im1 = m.pcolormesh(xx, yy, data[:,:].T, cmap=plt.cm.gray,  
                       vmin=sigma0_min, vmax=sigma0_max, shading='flat')
    
    x,y = m(lon_mooring,lat_mooring)
    m.plot(x,y,'ro',markersize=3)
    # annotate
    #m.drawcountries()
    m.drawcoastlines(linewidth=.5, color='yellow')
    m.drawlsmask(land_color="0.8")

    plt.savefig(path + file,dpi=600)
    plt.cla()