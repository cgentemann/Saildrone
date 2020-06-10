#!/usr/bin/env python
# coding: utf-8

# # This is the in situ and SSS collocation code. 
# # this is the part A of the program that searches for L2P files that have any data where cruise is


# Original script by: Chelle Gentemann
#            Edit by: Sotirios Skarpalezos


import os
import sys
import numpy as np
import xarray as xr
from pyresample import image, geometry, load_area, save_quicklook, SwathDefinition, area_def2basemap
from pyresample.geometry import GridDefinition
from pyresample.kd_tree import resample_nearest
from scipy import spatial
from read_routines import read_all_usv, get_filelist_slstr_l2p,get_orbital_data_slstr_l2p,rectangle_overlap


# Area for PyResample
# -------------------
'''some definitions'''
area_def = load_area('areas.cfg', 'pc_world_1km')
rlon = np.arange(-180, 180, .01)
rlat = np.arange(90, -90, -.01)

# Enter paths etc
# ---------------
# input_iusv_start = int(input("Enter start cruise processing number 0-10: "))
# input_iusv_end = int(input("Enter stop cruise processing number 0-10: "))
# adir_usv = str(input("Enter directory for USV data: "))
# adir_l1r = str(input("Enter directory for L1R data: "))

input_iusv_start = 0
input_iusv_end = 1
# Path where matchup files will be saved:
adir_out = '/data/users/ssk/saildrone_data/matchup_SLSTR/'
# Path pattern to select campaigns (Enter full path if you want one file):
dir_data_pattern = '/data/users/ssk/saildrone_data/*34_2019.nc'
# Path where satellite data are:
adir_l2p = '/net/isilon/ifs/arch/home/sstdev/Projects/ESA_CCI2/C3S/L2P/SLSTRA/'

# Open all campaigns as xarray datasets inside a dictionary:
data_dict = read_all_usv(dir_data_pattern)

# Loop through campaings
# ----------------------
for iname,name in enumerate(data_dict):
    file_save=[] # Initialize variable for each processing run
    ds_usv,name_usv = data_dict[name],name # Open saildrone campaign in ds_usv
    fileout = adir_out + name_usv +'_SLSTR_matchup.nc' # Set output file name
    
    # Search usv data
    # ---------------
    minday,maxday = ds_usv.time[0],ds_usv.time[-1] # Get campaign start and end dates
    usv_day = minday
    print('\n')
    print('Cruise start time:',minday.data)
    print('Cruise end time:',maxday.data,'\n')
    
    # Loop through days
    # -----------------
    while usv_day <= maxday:
#        usv_day = minday + np.timedelta64(11,'D') ######################### DEBUGGING LINE #####################################################
        # Subsample saildrone data for the day ± 1 day into ds_day
        ds_day = ds_usv.sel(time=slice(usv_day-np.timedelta64(1,'D'),usv_day+np.timedelta64(1,'D')))
        ilen = ds_day.time.size # Get the amount of saildrone observations for that day ± 1 day
        if ilen<1: # If there is no data, move on to the next day
            continue
        # We have saildrone data for this day
        # -----------------------------------
        # Find extreme coordinates of the saildrone subset data
        minlon,maxlon,minlat,maxlat = ds_day.lon.min().data,ds_day.lon.max().data,ds_day.lat.min().data,ds_day.lat.max().data
        # Get satelite files on current day
        filelist = get_filelist_slstr_l2p(adir_l2p, usv_day)

        print('\nDay:',usv_day.data,)
        print('----------------------------------')
        print('Number of granules on this day:',len(filelist))
        
        # Loop through swaths
        # -------------------
#        file_counter_no_overlap = 0
#        file_counter_no_data = 0
#        file_counter_processed = 0
        for file,file_idx in zip(filelist,np.arange(len(filelist))):
#            file = filelist[212] ########################################################### DEBUGGING LINE ###################################
            ds = xr.open_dataset(file)
            ds.close()
    
            amsr_lats = ds['lat'].data
            amsr_lons = ds['lon'].data
            
            # Correct for possible NaN values that are read as -2.14748365e+09
            amsr_lats[amsr_lats<-90] = np.nan
            amsr_lons[amsr_lons<-180] = np.nan
            amsr_lats_min = np.nanmin(amsr_lats)
            amsr_lats_max = np.nanmax(amsr_lats)
            amsr_lons_min = np.nanmin(amsr_lons)
            amsr_lons_max = np.nanmax(amsr_lons)
            
            # Get lat, lon of SLSTR granule:
#            xlat,xlon,sat_time,var_data=get_orbital_data_slstr_l2p(file)
#            amsr_lons = xlon.data
#            amsr_lats = xlat.data
            # Check if saildrone subset and SLSTR granule overlap each other:
            overlap_flag = rectangle_overlap(amsr_lons_min,amsr_lons_max,amsr_lats_min,amsr_lats_max,minlon,maxlon,minlat,maxlat)
            # If saildrone subset and SLSTR granule do not overlap, move on to the next granule
            if overlap_flag == False:
#                ds.close()
#                file_counter_no_overlap = file_counter_no_overlap + 1
                print('File '+str(file_idx+1)+': No overlap')
                continue
            # Else, get also time and data (SST)
            xlat,xlon,sat_time,var_data=get_orbital_data_slstr_l2p(file)
#            var_data = ds['sea_surface_temperature']
#            sat_time = ds['time'] + ds['sst_dtime']
#            ds.close()
            print('\nFile '+str(file_idx+1)+': OVERLAP')
            print('File name:',file)
            var_data = xr.DataArray.squeeze(var_data)
            amsr_data = np.squeeze(var_data.data)
            sat_time = np.squeeze(sat_time.data[:,:,0]).astype('datetime64[ms]')
            
            swath_def = SwathDefinition(amsr_lons, amsr_lats)
            
            
            # Resample swath to a fixed 0.01 x 0.01 grid, represented by the variable grid_def:
            # https://stackoverflow.com/questions/58065055/floor-and-ceil-with-number-of-decimals
            grid_def_lon_min = np.round(amsr_lons_min - 0.5 * 10**(-2), 2)
            grid_def_lon_max = np.round(amsr_lons_max + 0.5 * 10**(-2), 2)
            grid_def_lat_min = np.round(amsr_lats_min - 0.5 * 10**(-2), 2)
            grid_def_lat_max = np.round(amsr_lats_max + 0.5 * 10**(-2), 2)
            grid_def_lons = np.arange(grid_def_lon_min,grid_def_lon_max+0.01,0.01)
            grid_def_lats = np.arange(grid_def_lat_max,grid_def_lat_min-0.01,-0.01)
            grid_mesh_lons,grid_mesh_lats = np.meshgrid(grid_def_lons,grid_def_lats)
            
            # Since we have the lon and lat values for the area, we define a grid instead of an area:
            # https://pyresample.readthedocs.io/en/latest/geo_def.html#griddefinition
            grid_def = GridDefinition(lons=grid_mesh_lons,lats=grid_mesh_lats)
            
            # https://pyresample.readthedocs.io/en/latest/API.html#pyresample.kd_tree.resample_nearest
            result1 = resample_nearest(swath_def, amsr_data, grid_def, radius_of_influence=2000, fill_value=np.nan)
            
            # Save the resampled swath to the xarray dataset "da":
            # http://xarray.pydata.org/en/stable/data-structures.html
            da = xr.DataArray(result1,name='sat_data',coords={'lat':grid_def_lats,'lon':grid_def_lons},dims=('lat','lon'))
            
            # Subset the global grid to the area of the saildrone daily subset area:
            subset = da.sel(lat = slice(maxlat,minlat),lon=slice(minlon,maxlon))
            
            # Check for observations within this area:
            num_obs = np.isfinite(subset).sum()
            
            if num_obs<1: # If there is no satellite data within the saildrone daily area, move on to the next swath
#                file_counter_no_data = file_counter_no_data + 1
                print('No satellite data\n')
                continue
            
            # We have satellite data within the saildrone daily area
            # ------------------------------------------------------
            print('Satellite data detected, matching data...\n')
            # Drop points outside of saildrone data area for the specific day:
            usv_min_lon, usv_max_lon = ds_usv.lon.min().data - .5, ds_usv.lon.max().data + .5 # Min and max lon value of all saildrone data for the cruise
            usv_min_lat, usv_max_lat = ds_usv.lat.min().data - .5, ds_usv.lat.max().data + .5 # Min and max lat value of all saildrone data for the cruise
            cond = (xlon >= usv_min_lon) & (xlon <= usv_max_lon) # Find which swath lon are inside the saildrone observations margins
            sub_lon = xlon.where(cond) # True: inside saildrone margins, False: outside saildrone margins
            cond = (xlat >= usv_min_lat) & (xlat <= usv_max_lat) # Find which AMSR lat are inside the saildrone observations margins
            sub_lat = xlat.where(cond) # True: inside saildrone margins, False: outside saildrone margins

            ph0 = var_data.nj # Along swath dimension
            ph1 = var_data.ni # Across swath dimension
            amsr_time = sat_time # Time for each AMSR scan line
            
            ds = xr.Dataset({'time': (['phony_dim_0'], amsr_time),
                             'sst': (['phony_dim_0', 'phony_dim_1'], var_data),
                             'lat': (['phony_dim_0', 'phony_dim_1'], sub_lat.data),
                             'lon': (['phony_dim_0', 'phony_dim_1'], sub_lon.data)},
                            coords={'phony_dim_0': (['phony_dim_0'], ph0),
                                    'phony_dim_1': (['phony_dim_1'], ph1)})

            #stack xarray dataset then drop lon == nan
            ds2 = ds.stack(z=('phony_dim_0', 'phony_dim_1')).reset_index('z') # Reshape into a vector
            # Drop nan
            ds_dropa = ds2.where(np.isfinite(ds2.lon), drop=True)
            ds_drop = ds_dropa.where(np.isfinite(ds_dropa.lat), drop=True)
            
            # SO FAR:
            # -------
            # For each AMSR file:
            # - We throw away all observations that are outside the area of saildrone observations (ds_drop)
            
            amsr_lats = ds_drop.lat.data # Filter AMSR lat data
            amsr_lons = ds_drop.lon.data # Filter AMSR lon data
            inputdata = list(zip(amsr_lons.ravel(), amsr_lats.ravel())) # Make a list with coordinate tuples of filtered lats and lons
            tree = spatial.KDTree(inputdata) # So we are able to search for nearest neighbor of the tuple coordinates
#            orbit_time = ds.time.max().data - np.timedelta64(1, 'D') ################################################################################
#            orbit_time2 = ds.time.max().data + np.timedelta64(1, 'D') ###############################################################################
            orbit_time = ds.time.min().data - np.timedelta64(12, 'h')
            orbit_time2 = ds.time.max().data + np.timedelta64(12, 'h')
            usv_subset = ds_usv.sel(time=slice(orbit_time, orbit_time2))
            ilen = ds_usv.time.size
            for iusv in range(ilen): # Loop through all saildrone observations for the campaign
                if (ds_usv.time[iusv] < orbit_time) or (ds_usv.time[iusv] > orbit_time2):
                    continue
                pts = np.array([ds_usv.lon[iusv], ds_usv.lat[iusv]])
                #        pts = np.array([ds_usv.lon[iusv]+360, ds_usv.lat[iusv]])
                tree.query(pts, k=1)
                i = tree.query(pts)[1]
                rdist = tree.query(pts)[0]
                
                # don't use matchups more than 25 km away
                if rdist > .25:
                    continue
                # use .where to find the original indices of the matched data point
                # find by matching sss and lat, just randomly chosen variables, you could use any
                result = np.where((ds.sst == ds_drop.sst[i].data) & (ds.lat == ds_drop.lat[i].data))
                listOfCoordinates = list(zip(result[0], result[1]))
                if len(listOfCoordinates) == 0:
                    continue
                ii, jj = listOfCoordinates[0][0], listOfCoordinates[0][1]
                deltaTa = ((ds_usv.time[iusv] - ds.time[ii]).data) / np.timedelta64(1, 'm')
                if np.abs(deltaTa) < np.abs(ds_usv['deltaT'][iusv].data and ds.quality_flag[ii,jj] >= 3: #########################################################################
                    # Here add also check for quality flag ---> DONE
                    
                    ds_usv['deltaT'][iusv] = deltaTa
                    file_tail = os.path.basename(os.path.normpath(file))
                    ds_usv.slstr_name[iusv] = file_tail
                    ds_usv.slstr_dist[iusv] = rdist
                    ds_usv.slstr_scan[iusv] = ii
                    ds_usv.slstr_cell[iusv] = jj
                    ds_usv.slstr_quality_flag = ds.quality_flag[ii,jj]

        usv_day += np.timedelta64(1,'D')
#    df = xr.DataArray(file_save,name='filenames')
    ds_usv = ds_usv.rename({'TEMP_CTD_MEAN':'insitu.sea_surface_temperature','TEMP_CTD_STDDEV':'insitu.sst_uncertainty',
                             'TEMP_AIR_MEAN':'insitu.air_temperature','VWND_MEAN':'insitu.vwnd','UWND_MEAN':'insitu.uwnd',
                             'WAVE_SIGNIFICANT_HEIGHT':'insitu.sig_wave_height','SAL_MEAN':'insitu.salinity','CHLOR_MEAN':'insitu.chlor',
                             'BARO_PRES_MEAN':'insitu.baro_pres','RH_MEAN':'insitu.rel_humidity','GUST_WND_MEAN':'insitu.gust_wind',
                             'lat':'insitu.lat','lon':'insitu.lon','time':'insitu.time'})

    ds_usv.to_netcdf(fileout, format='NETCDF4')
    
    
    
    # Variable explanation
    # --------------------
    # ds_usv: Whole saildrone campaign
    # ds_day: Subset of saildrone campaign for the current day ± 1 day
    # da: Satellite swath resample in a global 0.1 x 0.1 grid
    # subset: Subset of da for the aea where we have saildrone data for a specific day
    # ds_drop: 
    
    
    
    