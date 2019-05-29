import sys
import snappy
from snappy import ProductIO
from snappy import HashMap

import os
from snappy import GPF
import glob

GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
HashMap = snappy.jpy.get_type('java.util.HashMap')

def do_mosaic(source):
    parameters = HashMap() 
    parameters.put('pixelSize', 200.0)
    parameters.put('resamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('mapProjection', "AUTO:42001")
    parameters.put('variables','Sigma0_HH')
    output = GPF.createProduct('SAR-Mosaic', parameters, source)

processed_path = 'D:/Project_Data/Arctic_PRIZE/Processed_Data/S1/'

text_file = open(processed_path + "list_dim.txt","r")
mosaic_files= text_file.readlines()
#mosaic_files = glob.glob(os.path.join(processed_path, '*HH.dim*'))
#print(mosaic_files)

products = []
for fl in mosaic_files:
    print(processed_path + fl)
    products.append(ProductIO.readProduct(processed_path + fl))

mosaic_data = do_mosaic(mosaic_files)
ProductIO.writeProduct(mosaic_data, 'mosaic', 'GeoTIFF')
