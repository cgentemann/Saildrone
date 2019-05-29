import sys
import snappy
from snappy import ProductIO
from snappy import HashMap

import os
from snappy import GPF
import glob

GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
HashMap = snappy.jpy.get_type('java.util.HashMap')


processed_path = 'D:/Project_Data/Arctic_PRIZE/Processed_Data/S1/'

#text_file = open(processed_path + "list_dim.txt","r")
#mosaic_files= ('S1A_EW_GRDM_1SDH_20170601T053330_20170601T053435_016836_01BFD7_A0B2_terrian_200mHH.dim', \
#               'S1A_EW_GRDM_1SDH_20170601T071215_20170601T071320_016837_01BFE1_35BF_terrian_200mHH.dim')
#print(mosaic_files)
mosaic_files = glob.glob(os.path.join('*HH.dim*'))
print(mosaic_files)

products = []
for fl in mosaic_files:
    products.append(ProductIO.readProduct(fl))
    print(fl)

### Mosaic 
parameters = HashMap() 
parameters.put('pixelSize', 200.0)
parameters.put('resampling', 'BILINEAR_INTERPOLATION')
#parameters.put('crs', "AUTO:42001")
parameters.put('variables','Sigma0_HH')
#parameters.put('westBound',15)
#parameters.put('eastBound',25)
#parameters.put('southBound',80)
#parameters.put('northBound',82.5)

mosaic_data = GPF.createProduct('SAR-Mosaic', parameters, products)

ProductIO.writeProduct(mosaic_data, 'mosaic', 'GeoTIFF')
