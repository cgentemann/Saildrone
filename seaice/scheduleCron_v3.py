#import schedule
import time
import os
from get_masie_file_v3 import get_extent
from put_masie_file_v1 import put_extent
from datetime import datetime
from send_email_extent_v2 import send_email_extent
from plot_ice_extent_v3 import plot_ice_extent
import shutil

now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Find users home directory
home = os.path.expanduser('~')
# Append data path to home directory
data_path = home+"/Project_Data/Arctic_PRIZE/Data/Ice_Extent/current/"
tools_path = home+"/Project_Data/Arctic_PRIZE/Data/Ice_Extent/Tools/"
    
def job_extent():
    import numpy as np
    f = 0
    to_path = "V:/download/PRIZE/"
    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    yday_now = datetime.now().timetuple().tm_yday
    yday_now = yday_now - 1
    yday_now_str = str(yday_now).zfill(3)
    filename = 'masie_all_r00_v01_2017'+yday_now_str+'_4km.tif'
    fig_file = 'masie_all_r00_v01_2017'+yday_now_str+'_4km.png'
    filelist = os.listdir(data_path)
    file_array = np.asarray(filelist)
    latest = np.where(file_array == filename)
	    
    if len(latest[0]) == 0:
        print("---no file in computer..."+now+yday_now_str)
        print("---checking... ftp site for new file..."+now)        
        f = get_extent(filename,data_path)
        #f=1
        if f == 1:
            print("---file found in ftp downloaded..."+filename)
            plot_ice_extent(filename,data_path,tools_path)
            print(fig_file)
            put_extent(fig_file)
            #send_email_extent(filename)
        else:
            print("---file NOT found in ftp..."+filename) 
    else:
        print('---file already exist in computer--@'+now)

    print("___ending processing...@"+now)

job_extent()
	
# whether extent file updated or not
# 0: not yet, 1: updated
# start from 13:00 BST

# 13:00 BST ------
#schedule.every(1).day.at("13:00").do(job_extent)

# 14:00 BST -----
#schedule.every(1).day.at("14:00").do(job_extent)

# 15:00 BST -----
#schedule.every(1).day.at("15:00").do(job_extent)

# 16:00 BST -----
#schedule.every(1).day.at("16:00").do(job_extent)

# 17:00 BST -----
#schedule.every(1).day.at("17:00").do(job_extent)

# 18:00 BST -----
#schedule.every(1).day.at("18:00").do(job_extent)

# 19:00 BST -----
#schedule.every(1).day.at("19:00").do(job_extent)

#while 1:
#    schedule.run_pending()
#    time.sleep(1)

