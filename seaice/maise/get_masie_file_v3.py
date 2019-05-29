
from ftplib import FTP 
import time
import numpy as np
#from datetime import datetime 
import shutil
#mport os


#ome = os.path.expanduser('~')
#o_path = home+"/Project_Data/Arctic_PRIZE/Data/Ice_Extent/current/"

#to_path = "~/Project_Data/Arctic_PRIZE/Data/Ice_Extent/current/"

def get_extent(filename,to_path):

    f = 0
    path = "/DATASETS/NOAA/G02186/geotiff/4km/all_surface/2017"

    #Open ftp connection
    ftp = FTP('sidads.colorado.edu','anonymous','p.b.j.hwang@gmail.com')
    ftp.cwd(path) #changing to /pub/unix

    data = []
    datelist = []
    filelist = []
    ftp.dir(data.append)

    for line in data:
        col = line.split()
        datestr = ' '.join(line.split()[5:8])
        if (col[8] != '.') and (col[8] != '..'):
            date = time.strptime(datestr, '%b %d %H:%M')
            datelist.append(date)
            filelist.append(col[8])

    file_array = np.asarray(filelist)
    
    latest = np.where(file_array == filename)
        
    if len(latest[0]) == 0:
        print("file has not been updated")
        f = 0 # file not found
        ftp.quit()
    else:
        indx = int(latest[0])
        filename = str(filelist[indx])
        print("file to download is %s" % filename)
        ftp.retrbinary('RETR %s' % filename, open(filename, 'wb').write)
        shutil.move(filename,to_path+filename)
        print("***Downloaded*** %s " % filename)
        f = 1 # file found
        ftp.quit()

    return f
