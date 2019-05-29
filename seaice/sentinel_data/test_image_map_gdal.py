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


def convertXY(xy_source, inproj, outproj):
    # function to convert coordinates

    shape = xy_source[0,:,:].shape
    size = xy_source[0,:,:].size

    print(shape)
    print(size)
    # the ct object takes and returns pairs of x,y, not 2d grids
    # so the the grid needs to be reshaped (flattened) and back.
    ct = osr.CoordinateTransformation(inproj, outproj)
    xy_target = np.array(ct.TransformPoints(xy_source.reshape(2, size).T)) #.T

    xx = xy_target[:,0].reshape(shape)
    yy = xy_target[:,1].reshape(shape)

    return xx, yy

path = 'D:/Project_Data/Arctic_PRIZE/Processed_Data/S1/'

file = 'S1B_EW_GRDM_1SDH_20170601T062150_20170601T062250_005853_00A430_9294_terrian_200m_subset_HH.tif'

ds = gdal.Open(path + file)


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
m = Basemap(projection='tmerc', lat_0=81, lon_0=18, llcrnrlon=15., \
            llcrnrlat=80.,urcrnrlon=25.,urcrnrlat=82, resolution='i')

# Create the projection objects for the convertion
# original (Albers)
inproj = osr.SpatialReference()
inproj.ImportFromWkt(project)
#inproj.ImportFromProj4(proj)

# Get the target projection from the basemap object
outproj = osr.SpatialReference()
outproj.ImportFromProj4(m.proj4string)

# Convert from source projection to basemap projection
#xx, yy = pyproj.transform(inproj, outproj)
#xx, yy = convertXY(xy_source, inproj, outproj)

#convert utm coordinates into lat/lon
myProj = Proj("+proj=utm +zone=34, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
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

# annotate
m.drawcountries()
m.drawcoastlines(linewidth=.5, color='yellow')

plt.savefig('world.png',dpi=600)