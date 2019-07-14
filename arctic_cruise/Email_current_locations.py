#!/usr/bin/env python
# coding: utf-8

# In[3]:


import urllib.request
import xarray as xr
import numpy as np
from datetime import datetime, date, time, timedelta
import urllib
import requests
import json
import smtplib


# In[4]:



#not useing this right now but consider putting instance here
def get_key(file_name):
    myvars = {}
    with open(file_name) as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            myvars[name.strip()] = str(var).rstrip()
    return myvars

file_key = "C:/Users/gentemann/Google Drive/f_drive/secret_keys/saildrone.txt"
saildrone_key = get_key(file_key)
file_key = "C:/Users/gentemann/Google Drive/f_drive/secret_keys/gmail_login.txt"
email_key = get_key(file_key)

# ## Use restful API to get USV locations

endtime = datetime.today().strftime('%Y-%m-%d')
starttime = (datetime.today() + timedelta(days=-5)).strftime('%Y-%m-%d')
#all_usv = ['1041','1033','1034','1035','1036','1037']
all_usv = ['1034','1035','1036','1037']
#get token
payload={'key': saildrone_key['key'], 'secret':saildrone_key['secret']}
headers={'Content-Type':'application/json', 'Accept':'application/json'}
url = 'https://developer-mission.saildrone.com/v1/auth'
res = requests.post(url, json=payload, headers=headers)
json_data = json.loads(res.text)
names=[]
inum_usv = len(all_usv)
ilen = 500 #len(usv_data['data'])
usv_lats = np.empty((ilen,inum_usv))*np.nan
usv_lons = np.empty((ilen,inum_usv))*np.nan
usv_time = np.empty((ilen,inum_usv))*np.nan
for iusv in range(inum_usv):
    str_usv = all_usv[iusv]
    url = 'https://developer-mission.saildrone.com/v1/timeseries/'+str_usv+'?data_set=vehicle&interval=5&start_date='+starttime+'&end_date='+endtime+'&order_by=desc&limit=500&offset=0'
    payload = {}
    headers = {'Accept':'application/json','authorization':json_data['token']}
    res = requests.get(url, json=payload, headers=headers)
    usv_data = json.loads(res.text)
    #print(usv_data.data)
    for i in range(ilen):
        usv_lons[i,iusv]=usv_data['data'][i]['gps_lng']
        usv_lats[i,iusv]=usv_data['data'][i]['gps_lat']
        usv_time[i,iusv]=usv_data['data'][i]['gps_time']
    names.append(str_usv)
xlons = xr.DataArray(usv_lons,coords={'time':usv_time[:,0],'trajectory':names},dims=('time','trajectory'))
xlats = xr.DataArray(usv_lats,coords={'time':usv_time[:,0],'trajectory':names},dims=('time','trajectory'))
ds_usv = xr.Dataset({'lon': xlons,'lat':xlats})


# In[5]:


msg_body=[]
for i in range(1):
    for j in range(inum_usv):
        dt = datetime.fromtimestamp(ds_usv.time[i].data)
        s = dt.strftime('%Y-%m-%d %H:%M:%S')
        msg = all_usv[j]+" "+s+" lon :{0:5.2f}, lat :{1:5.2f}    ".format(ds_usv.lon[i,j].data,ds_usv.lat[i,j].data)
        msg_body.append(msg)


# In[6]:



try:  
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
except:  
    print ('Something went wrong...')
sent_from = email_key['key']  
to = ['cgentemann@gmail.com', 'andy.chiodi@noaa.gov']  
subject = 'Daily Saildrone Position Update'  
body = msg_body
email_text = """\  
From: %s  
To: %s  
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)
try:  
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(email_key['key'], email_key['secret'])
    server.sendmail(sent_from, to, email_text)
    server.close()

    print('Email sent!')
except:  
    print('Something went wrong...')
    


# In[ ]:




