
from ftplib import FTP 
import logging
import time
import numpy as np
#from datetime import datetime 
import shutil

def get_extent(filename,to_path):

    logging.info("---checking... ftp site for new file..." + filename ) 

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
        logging.info("file has not been updated")
        f = 0 # file not found
        ftp.quit()
    else:
        indx = int(latest[0])
        filename = str(filelist[indx])
        logging.info("file to download is %s" % filename)
        ftp.retrbinary('RETR %s' % filename, open(filename, 'wb').write)
        shutil.move(filename,to_path+filename)
        logging.info("***Downloaded*** %s " % filename)
        f = 1 # file found
        ftp.quit()

    return f
