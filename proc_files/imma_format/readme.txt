Instructions on how to run the ICOADS conversion programs to convert data from IMMA1 format to netCDF 4 format.

*******************************************************************
All the codes are written in python and tested using python 2.6.6

Main program: Read_IMMA.py

Modules developed: IMMA2nc1.py, IMMA.py

Modeles from others: jdutil.py

Internal moduels called: netCDF4, numpy, uuid, time, os, re, datetime, fnmatch, gzip, tarfile
Please make sure your python has the required internal modules before run the program 
*******************************************************************

Step by step instructions

1. set up path
  1.1 Open Read_IMMA.py, 
	set up "fp_IMMA1" to the path where the IMMA1 data located 
     	set up "fp_nc" to the path where netCDF file will be saved
        if the IMMA1 data are still in .tar format, change "tar_extract" to 1
        if the IMMA1 data are in .gz format, do nothing. The program can read .gz files directly. Please do not uncompress the .gz files.
  1.2 Open IMMA2nc1.py,
        below several import commands, set up "fpath_default" to where the codes are saved

2. run the program using:
 	python Read_IMMA.py



Questions? please contact Zhankun.wang@noaa.gov    
          