#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os

adir = 'F:/data/clim_data/icoads/2010s/'
adir2 = 'F:/data/clim_data/icoads/2010s_subset/'
for root, dirs, files in os.walk(adir):
    for filename in files:
        #print(filename)
        file_out=filename[:-3]+'_subset.nc'
        ds=xr.open_dataset(adir+filename)
        ds.close()
        keep=['SST','SI','PT','SNC','DUPC','DUPS','OTZ','DOS','AT','II','ANC']
        for var in ds:
            if np.logical_not(var in keep):           
            #else:
                ds=ds.drop(var)

        cond = (ds.lat>50) & (ds.lat<80) & (ds.SNC==1) & (ds.DUPS==0) & (ds.lon>180) & (ds.lon<215)
        subset = ds.where(cond,drop=True)
        subset.to_netcdf(adir2+file_out)
        print(filename)


