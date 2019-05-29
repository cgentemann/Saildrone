import snappy
 
from snappy import ProductIO
from snappy import HashMap
 
import os   
from snappy import GPF
 
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
HashMap = snappy.jpy.get_type('java.util.HashMap')

data_path = 'D:/Project_Data/Arctic_PRIZE/Data/S1/'
temp_path = 'D:/Project_Data/Arctic_PRIZE/Temp/'
out_path = 'D:/Project_Data/Arctic_PRIZE/Processed_Data/S1/'
file1 = 'S1B_EW_GRDM_1SDH_20170601T062150_20170601T062250_005853_00A430_9294'

sentinel_1 = ProductIO.readProduct(data_path + file1 + '.zip')
print(sentinel_1)

### Calibration
pols = ['HH']
for p in pols:


    polarization = p    

    #### Speckle filter
    parameters = HashMap()
    parameters.put('sourceBands', 'Intensity_' + polarization)
    parameters.put('filter', 'Median')
    #parameters.put('numberOfLooks',1)
    #parameters.put('windowSize', 7)
    #parameters.put('sigma',0.9)
    #parameters.put('targetWindowSize',3)

    speckle_file = temp_path+ "speckle_" + polarization 
    speckle_data = GPF.createProduct("Speckle-Filter", parameters, sentinel_1) 
    ProductIO.writeProduct(speckle_data, speckle_file, 'BEAM-DIMAP')
    print('---end of speckle filtering---')


    ### Calibration
    parameters = HashMap() 
    parameters.put('outputSigmaBand', True) 
    parameters.put('sourceBands', 'Intensity_' + polarization) 
    parameters.put('selectedPolarisations', polarization) 
    parameters.put('outputImageScaleInDb', False)
      
    calib_file = temp_path + "calibrate_" + polarization 
    calib_data = GPF.createProduct("Calibration", parameters, speckle_data) 
    ProductIO.writeProduct(calib_data, calib_file, 'BEAM-DIMAP')
    print('---end of calibration---')

    ### SUBSET
 
    calibration = ProductIO.readProduct(calib_file + ".dim")    
    WKTReader = snappy.jpy.get_type('com.vividsolutions.jts.io.WKTReader')
 
    wkt = "POLYGON((22.587890625 79.92054779769452, 33.92578125 79.92054779769452, \
                    33.92578125 81.33484424149815, 22.587890625 81.33484424149815, \
                    22.587890625 79.92054779769452))"
 
    geom = WKTReader().read(wkt)
 
    subsettings = HashMap()
    subsettings.put('geoRegion', geom)
    subsettings.put('outputImageScaleInDb', False)
 
    subset_file = temp_path + "subset_" + polarization
    subset_data = GPF.createProduct("Subset", subsettings, calib_data)
    ProductIO.writeProduct(subset_data, subset_file, 'BEAM-DIMAP')
    print('---end of subset---')
      

    ### TERRAIN CORRECTION - EW Full 40 m
 
    parameters = HashMap()    
    parameters.put('demName', 'ACE2_5Min')
    parameters.put('externalDEMNoDataValue', 0.0)
    parameters.put('demResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('imgResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('pixelSpacingInMeter', 40.0)
    parameters.put('pixelSpacingInDegree', 3.593261136478086E-4)
    parameters.put('mapProjection', "AUTO:42001")    

    terrain_file = out_path + file1 + "_terrian_40m" + polarization
    terrain_data = GPF.createProduct('Terrain-Correction', parameters, subset_data)
    ProductIO.writeProduct(terrain_data, terrain_file, 'GeoTIFF')
    print('---end of terrain---')


    ### TERRAIN CORRECTION - EW Full 200 m
 
    parameters = HashMap()    
    parameters.put('demName', 'ACE2_5Min')
    parameters.put('externalDEMNoDataValue', 0.0)
    parameters.put('demResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('imgResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('pixelSpacingInMeter', 200.0)
    parameters.put('pixelSpacingInDegree', 0.001796630568239043)
    parameters.put('mapProjection', "AUTO:42001")    

    terrain_file = out_path + file1 + "_terrian_200m" + polarization
    terrain_data = GPF.createProduct('Terrain-Correction', parameters, subset_data)
    ProductIO.writeProduct(terrain_data, terrain_file, 'GeoTIFF')
    print('---end of terrain---')
