# -*- coding: utf-8 -*-
# Purpose: Python module for processing and saving IMMA1 to netCDF 4
# same shortnames are used as the IMMA1 data, please refere to IMMA1 documentation for more details  
# IMMA1 documentation is at https://rda.ucar.edu/datasets/ds548.0/#!docs
# History: developed by Zhankun Wang between Oct 2016 and May 2017 for the BEDI ICOADS project
# (c) NOAA National Centers for Environmental Information
# contact: zhankun.wang@noaa.gov  

import uuid
import time
import netCDF4
import numpy as np
import os
import jdutil

# change the path to where the program and documents are saved. one level above 
fpath_default = '/users/senyastein/Documents/GitHub/Saildrone/proc_files/imma_format'
#fpath_default = '/nodc/projects/tsg/zwang/ICOADS/codes'
# change to where the python codes saved
os.chdir(fpath_default)

time_fmt = "%Y-%m-%dT%H:%M:%SZ"

att_doc = 2
if att_doc == 1:
    f = open('%sTables_ICOADS.csv' %fpath_default, 'r')
    lines = f.readlines()
    lines = [x.rstrip("\r\n") for x in lines]
    f.close()
    No = [x.split(',')[0] for x in lines]
    length = [x.split(',')[1] for x in lines]
    abbr = [x.split(',')[2].upper() for x in lines]
    longname = [x.split(',')[3] for x in lines]
    min_values = [x.split(',')[4] for x in lines]
    max_values = [x.split(',')[5] for x in lines]
    units = [x.split(',')[6] for x in lines]
    comments = [x.split(',')[7:] for x in lines]
elif att_doc == 2:
    f = open('%sicoads_dsv.csv' %fpath_default, 'r')
    lines = f.readlines()
    lines = [x.rstrip("\r\n") for x in lines]
    lines = [x.rstrip("\xa0") for x in lines]
    f.close()
    ancillary = [x.split(',')[1] for x in lines]
    names = [x.split(',')[2] for x in lines]
    units = [x.split(',')[5] for x in lines]
    min_values = [x.split(',')[6] for x in lines]
    max_values = [x.split(',')[7] for x in lines] 
    longname = [x.split(',')[9] for x in lines]
    flagvalues = [x.split(',')[10] for x in lines]
    # flagvalues = [x.replace(' ',',') for x in flagvalues]
    flagmeanings = [x.split(',')[17] for x in lines]
    standardname = [x.split(',')[18] for x in lines]
    scaledtype = [x.split(',')[16] for x in lines]
    comments = [x.split(',')[19] for x in lines]
    keywords_list = [x.split(',')[22] for x in lines]
    abbr = [x.split('-')[0] for x in names]
    abbr_e = [x.split('-')[1] if '-' in x else x for x in names]
    flagvalues = [x if 'blank' not in x else '' for x in flagvalues]
else:
    print('Error: No proper variable attributes document is found!')
    

parameters  = {}
attachment = {}
atta_list = [0,1,5,6,7,8,9,95,96,97,98,99]
attachment['00'] = 'CORE'
parameters['00'] = ('YR','MO','DY','HR','LAT','LON','IM','ATTC','TI','LI','DS','VS','NID','II','ID','C1','DI','D','WI','W','VI','VV','WW','W1','SLP','A','PPP','IT','AT','WBTI','WBT','DPTI','DPT','SI','SST','N','NH','CL','HI','H','CM','CH','WD','WP','WH','SD','SP','SH')
attachment['01'] = 'ICOADS ATTACHMENT'
parameters['01'] = ('BSI','B10','B1','DCK','SID','PT','DUPS','DUPC','TC','PB','WX','SX','C2','SQZ','SQA','AQZ','AQA','UQZ','UQA','VQZ','VQA','PQZ','PQA','DQZ','DQA','ND','SF','AF','UF','VF','PF','RF','ZNC','WNC','BNC','XNC','YNC','PNC','ANC','GNC','DNC','SNC','CNC','ENC','FNC','TNC','QCE','LZ','QCZ')
attachment['05'] = 'IMMT-5/FM13 ATTACHMENT'
parameters['05'] = ('OS','OP','FM','IMMV','IX','W2','WMI','SD2','SP2','SH2','IS','ES','RS','IC1','IC2','IC3','IC4','IC5','IR','RRR','TR','NU','QCI','QI1','QI2','QI3','QI4','QI5','QI6','QI7','QI8','QI9','QI10','QI11','QI12','QI13','QI14','QI15','QI16','QI17','QI18','QI19','QI20','QI21','HDG','COG','SOG','SLL','SLHH','RWD','RWS','QI22','QI23','QI24','QI25','QI26','QI27','QI28','QI29','RH','RHI','AWSI','IMONO')
attachment['06'] = 'MODEL QUALITY CONTROL ATTACHMENT'
parameters['06'] = ('CCCC','BUID','FBSRC','BMP','BSWU','SWU','BSWV','SWV','BSAT','BSRH','SRH','BSST','MST','MSH','BY','BM','BD','BH','BFL')
attachment['07'] = 'SHIP METADATA ATTACHMENT'
parameters['07'] = ('MDS','C1M','OPM','KOV','COR','TOB','TOT','EOT','LOT','TOH','EOH','SIM','LOV','DOS','HOP','HOT','HOB','HOA','SMF','SME','SMV')
attachment['08'] = 'NEAR-SURFACE OCEANOGRAPHIC DATA ATTACHMENT'
parameters['08'] = ('OTV','OTZ','OSV','OSZ','OOV','OOZ','OPV','OPZ','OSIV','OSIZ','ONV','ONZ','OPHV','OPHZ','OCV','OCZ','OAV','OAZ','OPCV','OPCZ','ODV','ODZ','PUID')
attachment['09'] = 'EDITED CLOUD REPORT ATTACHMENT'
parameters['09'] = ('CCE','WWE','NE','NHE','HE','CLE','CME','CHE','AM','AH','UM','UH','SBI','SA','RI')
attachment['95'] = 'REANALYSES QC/FEEDBACK ATTACHMENT'
parameters['95'] = ('ICNR','FNR','DPRO','DPRP','UFR','MFGR','MFGSR','MAR','MASR','BCR','ARCR','CDR','ASIR')
attachment['96'] = 'ICOADS VALUE-ADDED DATABASE ATTACHMENT'
parameters['96'] = ('ICNI','FNI','JVAD','VAD','IVAU1','JVAU1','VAU1','IVAU2','JVAU2','VAU2','IVAU3','JVAU3','VAU3','VQC','ARCI','CDI','ASII')
attachment['97'] = 'ERROR ATTACHMENT'
parameters['97'] = ('ICNE','FNE','CEF','ERRD','ARCE','CDE','ASIE')
attachment['98'] = 'UNIQUE ID ATTACHMENT'
parameters['98'] = ('UID','RN1','RN2','RN3','RSA','IRF')
attachment['99'] = 'SUPPLEMENTAL DATA ATTACHMENT'
parameters['99'] = ('ATTE','SUPD')

def get_var_att(var):
    idx = abbr.index(var)
    if att_doc == 1:
	att = {'abbr':var,'longname':longname[idx],'min_v':min_values[idx],'max_v': max_values[idx],'unit':units[idx], 'comment': comments[idx]}
    elif att_doc == 2:
	att = {'abbr':var,'ancillary':ancillary[idx],'standardname':standardname[idx],'scaledtype':scaledtype[idx],'longname':longname[idx],'min_v':min_values[idx],'max_v': max_values[idx],'unit':units[idx], 'comment': comments[idx], 'flagvalues': flagvalues[idx], 'flagmeanings':flagmeanings[idx]}
    else:
	print('Error: No attribute document found.')
    return att

def get_ancillary(anc_QC, check_list):
    var = anc_QC.split(';')
    var = [x.split('-')[0].strip() for x in var]
    var = [x for x in var if x in check_list ]
    return ' '.join(var)

def getParameters(i):
    return parameters["%02d" % i]


def save(out_file,data, **kwargs):
    def duration(seconds):
	t= []
	for dm in (60, 60, 24, 7):
		seconds, m = divmod(seconds, dm)
		t.append(m)
	t.append(seconds)
	return ''.join('%d%s' % (num, unit)
			 for num, unit in zip(t[::-1], 'W DT H M S'.split())
			 if num)
    def get_keywords(data):
	keywords = []
	for var in data.data.keys():
	    if var in abbr:
		idx = abbr.index(var)
		if len(keywords_list[idx])>0:
		    keywords.append(keywords_list[idx])
		    # print var, keywords_list[idx]  
	keywords = list(set(keywords))
	keywords = ['Earth Science > %s' %x for x in keywords]														      
	keywords = ', '.join(keywords)
	return keywords

    def Add_gattrs(ff):
	lon_min = min(data['LON'])
	lon_max = max(data['LON'])
	lat_min = min(data['LAT'])
	lat_max = max(data['LAT'])
	start_time = min(data.data['Julian'])
	end_time = max(data.data['Julian'])
	dur_time = (end_time-start_time)*24.0*3600.0
	start_time = jdutil.jd_to_datetime(start_time)
	start_time_s = "%s-%02d-%02dT%02d:%02d:%02dZ" %(start_time.year,start_time.month,start_time.day,start_time.hour,start_time.minute,start_time.second)
	end_time = jdutil.jd_to_datetime(end_time)
	end_time_s = "%s-%02d-%02dT%02d:%02d:%02dZ" %(end_time.year,end_time.month,end_time.day,end_time.hour,end_time.minute,end_time.second)
	version = out_file.split('_')[1]
	#start_time_s = time.strftime(time_fmt,time.gmtime(float(start_time)))
	#end_time_s = time.strftime(time_fmt,time.gmtime(float(end_time)))
        ff.ncei_template_version = "NCEI_NetCDF_Point_Template_v2.0"
        ff.featureType = "point"
	ff.title = "International Comprehensive Ocean-Atmosphere Data Set (ICOADS) %s data collected from %s to %s." %(version, start_time_s, end_time_s) 
	ff.summary = "This file contains ICOADS %s data in netCDF4 format collected from %s to %s. The International Comprehensive Ocean-Atmosphere Data Set (ICOADS) offers surface marine data spanning the past three centuries, and simple gridded monthly summary products for 2-degree latitude x 2-degree longitude boxes back to 1800 (and 1degreex1degree boxes since 1960)--these data and products are freely distributed worldwide. As it contains observations from many different observing systems encompassing the evolution of measurement technology over hundreds of years, ICOADS is probably the most complete and heterogeneous collection of surface marine data in existence." %(version, start_time_s, end_time_s)
	ff.keywords = get_keywords(data);
        ff.Conventions = "CF-1.6, ACDD-1.3"
        ff.id = out_file.split('.nc')[0].replace('IMMA1','ICOADS')
        ff.naming_authority = "gov.noaa.ncei"
        #ff.source = "http://rda.ucar.edu/data/ds548.0/imma1_r3.0.0/%s.tar" %out_file.split('-')[0]
	ff.source = "%s.gz" %out_file.split('.nc')[0]
	ff.processing_level = "Restructured from IMMA1 format to NetCDF4 format."
        ff.acknowledgement = "Conversion of ICOADS data from IMMA1 to netCDF format by NCEI is supported by the NOAA Big Earth Data Initiative (BEDI)."
        ff.license = "These data may be redistributed and used without restriction."
        ff.standard_name_vocabulary = "CF Standard Name Table v31"
        ff.date_created =  time.strftime(time_fmt,time.gmtime())
        ff.creator_name = "NCEI"
        ff.creator_email = "ncei.info@noaa.gov"
        ff.creator_url = "https://www.ncei.noaa.gov/"
        ff.institution = "National Centers for Environmental Information (NCEI), NOAA"
        ff.project = "International Comprehensive Ocean-Atmosphere Data Set (ICOADS) Project"
        ff.publisher_name = "NCEI"
        ff.publisher_email = "ncei.info@noaa.gov"
        ff.publisher_url = "https://www.ncei.noaa.gov/"
        ff.geospatial_bounds = "POLYGON ((%.4f %.4f,%.4f %.4f,%.4f %.4f,%.4f %.4f,%.4f %.4f))" %(lon_min,lat_min,lon_min,lat_max,lon_max,lat_max,lon_max,lat_min,lon_min,lat_min)
        ff.geospatial_bounds_crs = "EPSG:4326"
        ff.geospatial_lat_min = float("%.4f" %(lat_min))
        ff.geospatial_lat_max = float("%.4f" %(lat_max)) 
        ff.geospatial_lon_min = float("%.4f" %(lon_min))
        ff.geospatial_lon_max = float("%.4f" %(lon_max)) 
        ff.geospatial_lat_units = "degrees_north"
        ff.geospatial_lon_units = "degrees_east"
        ff.time_coverage_start = start_time_s
        ff.time_coverage_end = end_time_s
        ff.time_coverage_duration = 'P' + duration(dur_time)
        ff.time_coverage_resolution = "vary"
        ff.uuid = str(uuid.uuid4())
        ff.sea_name = "World-Wide Distribution"
        ff.creator_type = "group"
        ff.creator_institution = "NOAA National Centers for Environmental Information (NCEI)"
        ff.publisher_type = "institution"
        ff.publisher_institution = "NOAA National Centers for Environmental Information (NCEI)"
        ff.program = ""
	ff.contributor_name = "Zhankun Wang; ICOADS team"
	ff.contributor_role = "ICOADS Data Conversion to NetCDF; ICOADS IMMA1 Data Provider"
        ff.date_modified = time.strftime(time_fmt,time.gmtime())
        ff.date_issued = time.strftime(time_fmt,time.gmtime())
        ff.date_metadata_modified = time.strftime(time_fmt,time.gmtime())
        ff.product_version = "ICOADS %s netCDF4" %version
        ff.keywords_vocabulary = "Global Change Master Directory (GCMD) 2015. GCMD Keywords, Version 8.1."
	ff.cdm_data_type = 'Point'
	#ff.metadata_link = 'http://rda.ucar.edu/datasets/ds548.0/#!docs'
	ff.metadata_link = ''
	if len(set(data.data['IM'])) == 1:
	    ff.IMMA_Version = str(data.data['IM'][0])
	else: 
	    print('%s: check IMMA version' %out_file)
	if len(set(data.data['RN1'])) == 1:
	    ff.Release_Number_Primary = str(data.data['RN1'][0])
	else: 
	    print('%s: check Release_Number_Primary' %out_file)
	if len(set(data.data['RN2'])) == 1:
	    ff.Release_Number_Secondary = str(data.data['RN2'][0])
	else: 
	    print('%s: check Release_Number_Secondary' %out_file)
	if len(set(data.data['RN3'])) == 1:
	    ff.Release_Number_Tertiary = str(data.data['RN3'][0])
	else: 
	    print('%s: check Release_Number_Tertiary' %out_file)
	if len(set(data.data['RSA'])) == 1:
	    ff.Release_status_indicator = str(data.data['RSA'][0])
	else: 
	    print('%s: check RSA' %out_file)
	#ff.comment = ""      
	ff.references = 'http://rda.ucar.edu/datasets/ds548.0/docs/R3.0-citation.pdf'
        ff.history = time.strftime(time_fmt,time.gmtime()) + ": Converted from IMMA1 format to netCDF4 format by Z.W. "

    fpath = kwargs.get('fpath')
    if fpath is None:
	fpath = fpath_default
    #ftxt = open("%s%s.txt" %(fpath,out_file[0:-3]), 'w')
    #ftxt.write('Saving to %s ...\n' %out_file); 
    ff = netCDF4.Dataset(fpath + out_file.replace('IMMA1','ICOADS'), 'w', format='NETCDF4')
    Add_gattrs(ff)
    

    ff.createDimension('obs',len(data.data['YR']))
    '''
    # save time in Julian Days
    timein = ff.createVariable('time','f8',('obs',),zlib=True,complevel=4)
    timein.long_name = "time" 
    timein.standard_name = "time" 
    timein.units = "days since -4713-1-1 12:0:0 " 
    timein.calendar = "julian" 
    timein.axis = "T" 
    timein.comment = "Julian days since noon on January 1, 4713 BC. Missing values of date (DD in date) are replaced by 0 and missing values in HR are filled with 0.0 in this calculation. See actural values in date, HR for reference."  
    timein[:] = data.data['Julian'][:]
    '''
    # save time in Julian Days since the beginning of ICOADS data: 1662-10-15 12:00:00
    timein = ff.createVariable('time','f8',('obs',),zlib=True,complevel=4)
    timein.long_name = "time" 
    timein.standard_name = "time" 
    timein.units = "days since 1662-10-15 12:00:00" 
    timein.calendar = "julian" 
    timein.axis = "T" 
    timein.comment = "Julian days since the beginning of the ICOADS record, which is 1662-10-15 12:00:00. Missing values of date (DD in date) are replaced by 0 and missing values in HR are filled with 0.0 in this calculation. See actual values in date, HR for reference."  
    timein[:] = data.data['Julian1'][:]


    # save date in YYYYMMDD
    ff.createDimension('DATE_len',len(data.data['DATE'][0]))
    date = ff.createVariable('date','S1',('obs','DATE_len',),zlib=True,complevel=4)
    date.long_name = "date in YYYYMMDD" 
    #date.valid_min = '16000101'
    #date.valid_max = '20241231'
    date.format = 'YYYYMMDD'
    #date.axis = "T" 
    date.comment = "YYYY: four digital year, MM: two digital month and DD: two digital date. Missing values of DD have been filled with 99."  
    date[:] = [netCDF4.stringtochar(np.array(x)) for x in data.data['DATE']]
    #print data.data['YR']
    crsout = ff.createVariable('crs','i')
    crsout.grid_mapping_name = "latitude_longitude"
    crsout.epsg_code = "EPSG:4326"
    crsout.semi_major_axis = 6378137.0
    crsout.inverse_flattening = 298.257223563
    #crsout.comment = ''
    dim_list = []
    dim_dir = []
    exclusives = ['YR','MO','DY','SUPD','IM','ATTC','ATTE','RN1','RN2','RN3','RSA']
    '''
    exclusives_2 = ['CDE','CDI','YR','MO','DY','SUPD','IM','ATTC','ATTE','RN1','RN2','RN3','RSA','ICNR','FNR','DPRO','DPRP','UFR','MFGR','MFGSR','MAR','MASR','BCR','ARCR','CDR','ASIR'] 
    for atta in atta_list:
	var_list = getParameters(atta)
	for var in var_list:
	  if var in exclusives_2:
	      pass
	  else:
	    print var
	    att = get_var_att(var)
	    if 'flagvalues' in att:
		if len(att['flagvalues']) > 0:
		    print var, att['flagvalues'], att['flagmeanings']
		    foo = att['flagvalues'].split(' ')
		    foo_m = att['flagmeanings'].split(' ')
		    for x,y in zip(foo,foo_m): print('%s: %s' %(x,y))
    '''
    for atta in atta_list:
	var_list = getParameters(atta)
	for var in var_list:
	    if var in data.data.keys():
		if var in exclusives:
		    pass
		else:
		    start = time.time()
		    #ftxt.write('%s start at %s. ' %(var,time.strftime(time_fmt,time.gmtime()))); 
		    index = [i for i, x in enumerate(data.data[var]) if x is not None]
		    # print var,data[var],index[0],data.data[var][index[0]]
		    
		    if type(data.data[var][index[0]]) is int:
	    
			dataout = ff.createVariable(var,'i2',('obs',),fill_value = -99,zlib=True,complevel=4)
			#dataout = ff.createVariable(var,'f4',('obs',),zlib=True,complevel=4)
			dataout[index] = [data.data[var][idx] for idx in index]
		    elif type(data.data[var][index[0]]) is float:
			if var == 'LAT':
			    dataout = ff.createVariable('lat','f4',('obs',),zlib=True,complevel=4)
			elif var == 'LON':
			    dataout = ff.createVariable('lon','f4',('obs',),zlib=True,complevel=4)
			else:
			    dataout = ff.createVariable(var,'f4',('obs',),fill_value = float(-9999),zlib=True,complevel=4)
			dataout[index] = [data.data[var][idx] for idx in index]
		    elif type(data.data[var][index[0]]) is str:
			#print var
			if var == 'SUPD':
			    #ll = max([len(x) if x is not None else 0 for x in data.data[var] ])
			    #data.data[var] = [x.ljust(ll) if x is not None else None for x in data.data[var]]
			    pass
			else:
			    ll = len(data.data[var][index[0]])
			    if ll not in dim_list:
				ff.createDimension('%s_len' %var,ll)
				dataout = ff.createVariable(var,'S1',('obs','%s_len' %var,),zlib=True,complevel=4)
				dim_list.append(ll)
				dim_dir.append(var)
			    else:
				idx = dim_list.index(ll)
				dataout = ff.createVariable(var,'S1',('obs','%s_len' %dim_dir[idx],),zlib=True,complevel=4)  
			    dataout[index] = [netCDF4.stringtochar(np.array(data.data[var][idx])) for idx in index]
		    else:
			print var, type(data.data[var][index[0]])
		    
		    att = get_var_att(var)
		    if 'standardname' in att:
			if len(att['standardname']) >0: dataout.standard_name = att['standardname'] 
		    dataout.long_name = att['longname'] if len(att['longname']) > 0 else ""
		    if len(att['unit']) > 0: dataout.units = att['unit']
		    if len(att['min_v']) > 0: 
			if 'int' in att['scaledtype']: 
			    dataout.valid_min = np.int16(att['min_v'])
			elif 'double' in att['scaledtype']: 
			    dataout.valid_min = float(att['min_v'])
			else:
			    dataout.valid_min = float(att['min_v'])
		    if len(att['max_v']) > 0: 
			if 'int' in att['scaledtype']: 
			    dataout.valid_max = np.int16(att['max_v'])
			elif 'double' in att['scaledtype']: 
			    dataout.valid_max = float(att['max_v'])
			else:
			    dataout.valid_max = float(att['max_v'])
		    if var == 'LAT': dataout.axis = 'Y'
		    if var == 'LON': dataout.axis = 'X'
		    #if len(att['min_v']) > 0:
		    #	dataout.scale_factor = 1. 
		    #	dataout.add_offset = 0. 
		    if 'flagvalues' in att:
			if len(att['flagvalues']) >0: 
			    foo = att['flagvalues'].split(' ')
			    dataout.flag_values = [np.int16(x) for x in foo] 
			if len(att['flagmeanings']) >0: dataout.flag_meanings = att['flagmeanings'] 
		    if var != 'LAT' and var != 'LON':
			dataout.coordinates = "time lat lon" 
			dataout.grid_mapping = "crs" 
			dataout.cell_methods = "time: point" 
			if len(att['comment']) > 0: dataout.comment = att['comment'] 
		    if len(get_ancillary(att['ancillary'],data.data.keys())) > 0: dataout.ancillary_variables = get_ancillary(att['ancillary'],data.data.keys())

		    
		    end = time.time()
		    #print var, end-start
		    #ftxt.write('Time used = %s sec\n' %(end-start)); 
	#dataout.standard_name = "sea_surface_temperature" 
	#dataout.long_name = "Sea surface temperature" 
	#dataout.units = "degree_Celsius" 
	
    #ftxt.write('Done with %s' %out_file)
    ff.close()
    #ftxt.close()



