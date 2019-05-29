
from ftplib import FTP 
from pathlib import Path
import logging

def put_extent(filename,in_path):

    upload_file = Path(in_path+filename)
    if upload_file.is_file():

	logging.info("Found figure to upload "+filename)

        #pen ftp connection
        ftp = FTP('safari.sams.ac.uk','iceplots','1c3pl0t5')

        logging.info("Figure to upload is %s" % filename)
        file = open (in_path+filename,'rb')
        ftp.storbinary('STOR ' + filename, file)
        logging.info("***uploaded*** %s " % filename)
        file.close()
        ftp.quit()

    else:
        logging.info('Figure not found to upload '+ filename)

