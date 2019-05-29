
from ftplib import FTP 
from pathlib import Path

def put_extent(filename):

    upload_file = Path(filename)
    if upload_file.is_file():

	print("Found the file")

        #Open ftp connection
        ftp = FTP('safari.sams.ac.uk','iceplots','1c3pl0t5')

        #print("file to upload is %s" % filename)
        file = open (filename,'rb')
        ftp.storbinary('STOR ' + filename, file)
        #print("***uploaded*** %s " % filename)
        file.close()
        ftp.quit()

    else:
        #print("file not found %s" % filename)
        f = 1

    return 
