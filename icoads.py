#!/usr/bin/env python
# coding: utf-8

# In[1]:


import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import os
import timeit

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

        start = timeit.timeit()
        cond = (ds.lat>70) & (ds.SNC==1) & (ds.DUPS==0)
        subset = ds.where(cond,drop=True)
        end = timeit.timeit()
        print(start-end)

        start = timeit.timeit()
        cond = (ds.lat>70) 
        subset = ds.where(cond,drop=True)
        cond = (subset.SNC==1) 
        subset = subset.where(cond,drop=True)
        cond = (ds.DUPS==0)
        subset = subset.where(cond,drop=True)
        end = timeit.timeit()
        print(start-end)

        subset.to_netcdf(adir2+file_out)
        print(filename)


