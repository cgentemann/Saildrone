#! /usr/bin/python
#### -*- coding: utf-8 -*-
"""
Purpose: Read in ICOADS 3.0 IMMA1 data and convert them to netCDF4 format
Usage: python Read_IMMA.py
History: Created by Zhankun Wang on 10/15/2016
(c) NOAA National Centers for Environmental Information
Contacts: Zhankun.Wang@noaa.gov
"""
import IMMA
import IMMA2nc1
import time, datetime
import numpy as np
import fnmatch, os
import gzip, tarfile
import jdutil

# define class    
class ICOADS(object):
    def __init__(self):          # Standard instance object
        self.attachments = []    # List of attachments in this instance
	self.attachments_list = {'c5':[],'c6':[],'c7':[],'c8':[],'c9':[],'c95':[],'c96':[],'c97':[],'c98':[],'c99':[]}
        self.data = {}           # Dictionary to hold the parameter values
	self.data_compressed = {}
	self.sec_start_index = {}
	self.sec_len = {}
	for atta in atta_list:
	    var_list = getParameters(atta)
	    for var in var_list:
		self.data[var] = []	  
# Getter for instance parameters
    def __getitem__(self, key): return self.data[key]

    def save(self,record,i):
	for var in record.data.keys():
	    self.data[var].append(record[var])
	if 5 in record.attachments: self.attachments_list['c5'].append(i)
	if 6 in record.attachments: self.attachments_list['c6'].append(i)
	if 7 in record.attachments: self.attachments_list['c7'].append(i)
	if 8 in record.attachments: self.attachments_list['c8'].append(i)
	if 9 in record.attachments: self.attachments_list['c9'].append(i)
	if 95 in record.attachments: self.attachments_list['c95'].append(i)
	if 96 in record.attachments: self.attachments_list['c96'].append(i)
	if 97 in record.attachments: self.attachments_list['c97'].append(i)
	if 98 in record.attachments: self.attachments_list['c98'].append(i)
	if 99 in record.attachments: self.attachments_list['c99'].append(i)

    def remove_empty(self):
	for var in self.data.keys():
	    if not self.data[var]: del self.data[var]
    def remove_none(self):
	for var in self.data.keys():
	    if all(x is None for x in self.data[var]): del self.data[var]
    def check_qc(self):
	for var in ['SF','AF','UF','VF','PF','RF']:
	    if len(set(self.data[var])) == 1 and 15 in set(self.data[var]) : del self.data[var]
	for var in ['ZNC', 'WNC', 'BNC', 'XNC', 'YNC', 'PNC', 'ANC', 'GNC', 'DNC', 'SNC', 'CNC', 'ENC', 'FNC', 'TNC']:
	    if len(set(self.data[var])) == 1 and 10 in set(self.data[var]): del self.data[var]
	for var in ['QI%s' %i for i in range(1,30)]:
	    if var in self.data.keys():
		if len(set(self.data[var])) == 1 and 9 in set(self.data[var]): del self.data[var]

    def extend(self):
	# filled missing values with Nones to make all the variables have the same length as time. 
	# have to do this become the attachments might change from line to line, the missing values need to filled in. 
	for atta in atta_list[2:]:
	    var_list = getParameters(atta)
	    for var in var_list:
		if var in self.data.keys():
		    foo = [None]*len(data.data['YR'])
		    for i_individual,i_all in enumerate(self.attachments_list['c%s' %atta]):
			#print var, len(foo),i_all,i_individual
			foo[i_all] = self.data[var][i_individual]
		    self.data[var][:] = foo[:]

    def time2sec(self):
	def get_min(hr):
	    return int((hr-int(hr))*60.0)
	def get_msec(hr):
	    minute = (hr-int(hr))*60.0
	    second = (minute-int(minute))*60.0
	    return int((second-int(second))*1000000.0)
	def get_sec(hr):
	    minute = (hr-int(hr))*60.0
	    return int((minute-int(minute))*60.0)
	#ss = 23.45
	#print get_min(ss),get_sec(ss), get_msec(ss)
	if 'DY' not in self.data.keys(): self.data['DY'] = [None] * len(self.data['YR'])
	years = [x if x is not None else 0 for x in self.data['YR']]
	months = [x if x is not None else 0 for x in self.data['MO']]
	days = [x if x is not None else 1 for x in self.data['DY']]
	hours = [int(x) if x is not None else 0 for x in self.data['HR']]
	minutes = [get_min(x) if x is not None else 0 for x in self.data['HR']]
	seconds = [get_sec(x) if x is not None else 0 for x in self.data['HR']]
	mseconds = [get_msec(x) if x is not None else 0 for x in self.data['HR']]
	date = ['%s%02d%02d' %(x,y,z) if z is not None else '%s%02d99' %(x,y) for x,y,z in zip(self.data['YR'],self.data['MO'],self.data['DY'])]
	self.data['DATE'] = date
	#print years,months,days,hours,minutes,seconds,mseconds
	#self.data['SECONDS'] = [time.mktime(datetime.datetime(year,month,day,hour,minute,second,msecond).timetuple()) for year,month,day,hour,minute,second,msecond in zip(years,months,days,hours,minutes,seconds,mseconds)]
	self.data['Julian'] = [jdutil.date_to_jd(year,month,day+jdutil.hmsm_to_days(hour=hour,minute=minute,sec=second,micro=msecond)) for year,month,day,hour,minute,second,msecond in zip(years,months,days,hours,minutes,seconds,mseconds)]
	# julian day of 1662-10-15 12:00:00 = 2328381
	self.data['Julian1'] = [x-2328381 for x in self.data['Julian']]

	return
    
    def compress(self):
	for var in self.data.keys():
	    index = [i for i, x in enumerate(self.data[var]) if x is not None ]
	    self.data_compressed[var] = [x for x in self.data[var] if x is not None]
	    diff_index = np.diff(index)
	    sec_len = 1
	    start = [index[0]]
	    length = []
	    for x,y in zip(index[1:],diff_index):
		if y == 1:
		    sec_len+=1
		    
		else:
		    start.append(x)
		    length.append(sec_len)
		    sec_len = 1
	    length.append(sec_len)
	    #print var,self.data[var], start, stop
	    self.sec_start_index[var] = start
	    self.sec_len[var] = length	    
	return

def getParameters(i):
    return parameters["%02d" % i]

def extract_tar(fpath):
    # get list of tar files and extract them to designed folder
    files = [d for d in os.listdir('%s' % fpath) if fnmatch.fnmatch(d,'*.tar')] 
    files.sort()
    for x in files:
	tar = tarfile.open('%s%s' %(fpath,x))
	tar.extractall('%s' % fpath)
	tar.close()  

# define parameters
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

# set up path
fp = '/nodc/projects/tsg/zwang/ICOADS/'
# change to IMMA1 data located
fp_IMMA1 = '%sIMMA1/' %fp
# change to path where to save the data 
fp_nc = '%sNetCDF/' %fp

# extract tar files to gz files
# change tar_extract to 1 if the IMMA1 files are in tar format
tar_extract = 0
if tar_extract == 1:
    extract_tar(fp_IMMA1)

# get a list of gz files inside fp_IMMA1
# you can also manually input the file names that need to be processed.
# e.g. files = [IMMA1_R3.0.0_2000-01.gz IMMA1_R3.0.0_2010-03.gz]  
files = [d for d in os.listdir('%s' %fp_IMMA1) if fnmatch.fnmatch(d,'*.gz')] 
files.sort()

#files = files[0:2]
#files = ['IMMA1_R3.0.0_1823-06.gz']
# print files

# option 1
# use the 'processed_files.txt' to get a list of the processed files
# save the files that have been processed into 'processed_files.txt' and also save the time used to convert each file. 
info_filename = 'processed_files.txt'
if os.path.isfile('%s%s' %(fp_nc,info_filename)):
    ff_info = open('%s%s' %(fp_nc,info_filename),'r')
    processed_files = [x.split(":")[0] for x in ff_info.readlines() if 'time' in x]
    # print processed_files
    ff_info.close()
    ff_info = open('%s%s' %(fp_nc,info_filename),'a')
else:
    ff_info = open('%s%s' %(fp_nc,info_filename),'w')
    processed_files = []
# option 2
# use the actural files in the NetCDF folder to get a list of the processed_files
# For some reasons, the processed_files.txt" was saved only once a while. 
#processed_files = ['%s.gz' %d.split('.nc')[0].replace('ICOADS','IMMA1') for d in os.listdir('%s' %fp_nc) if fnmatch.fnmatch(d,'ICOADS_*.nc')] 
#processed_files.sort()
processed_files = processed_files[0:-1]
#processed_files = []

for fin in files:
    #print fin
    if fin not in processed_files:
	#print fin
	ts = time.gmtime()
	# save filename to processed_files.txt
	ff_info.write('%s: %s ' %(fin, time.strftime("%Y-%m-%d %H:%M:%S",ts))) 
	num_lines = sum(1 for line in gzip.open('%s%s' %(fp_IMMA1, fin))) #calculate how many data records in the file
	fhIn = gzip.open('%s%s' %(fp_IMMA1,fin),'rt') # open file
	data= ICOADS() #initialize the data
	# processing each record
	for i in range(num_lines):
	    record = IMMA.read(fhIn)
	    data.save(record,i)
	data.time2sec() # convert time to days since the reference time 
	data.remove_empty() # remove empty variables
	data.remove_none()  # remove variables with all Nones
	data.check_qc() # remove qc with only missing flag values
	data.extend() # fill missing values with None 
	fhIn.close()
	IMMA2nc1.save('%s.nc' %fin.split('.gz')[0],data, fpath = fp_nc) # save data to nc file
	te = time.gmtime()
	ff_info.write('%s time used = %s Min\n' %(time.strftime("%Y-%m-%d %H:%M:%S",te),(time.mktime(te)-time.mktime(ts))/60.0)) 
ff_info.close()   


