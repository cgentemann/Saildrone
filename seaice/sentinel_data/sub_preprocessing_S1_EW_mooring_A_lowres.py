import snappy
 
from snappy import ProductIO
#from snappy import HashMap
 
#import os   
from snappy import GPF


def preprocessing_S1_EW(file1,data_path,temp_path,out_path_hires,out_path_lowres,polarization):
    
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    HashMap = snappy.jpy.get_type('java.util.HashMap')

    sentinel_1 = ProductIO.readProduct(data_path + file1 + '.zip')
    print(sentinel_1)
    
    ### remove_thermal_noise
    parameters = HashMap() 
    parameters.put('selectedPolarisations', polarization)
    thermal_noise_data = GPF.createProduct('ThermalNoiseRemoval', parameters, sentinel_1)
    
    ### remove_GRD_border_noise
    parameters = HashMap() 
    parameters.put('selectedPolarisations', polarization)
    border_noise_data = GPF.createProduct('Remove-GRD-Border-Noise', parameters, thermal_noise_data)

    #### Speckle filter
    parameters = HashMap()
    parameters.put('sourceBands', 'Intensity_' + polarization)
    parameters.put('filter', 'Median')
    #parameters.put('numberOfLooks',1)
    #parameters.put('windowSize', 7)
    #parameters.put('sigma',0.9)
    #parameters.put('targetWindowSize',3)

    #speckle_file = temp_path+ "speckle_" + polarization 
    speckle_data = GPF.createProduct("Speckle-Filter", parameters, border_noise_data) 
    #ProductIO.writeProduct(speckle_data, speckle_file, 'BEAM-DIMAP')
    print('---end of speckle filtering---')


    ### Calibration
    parameters = HashMap() 
    parameters.put('outputSigmaBand', True) 
    parameters.put('sourceBands', 'Intensity_' + polarization) 
    parameters.put('selectedPolarisations', polarization) 
    parameters.put('outputImageScaleInDb', False)
      
    #calib_file = temp_path + "calibrate_" + polarization 
    calib_data = GPF.createProduct("Calibration", parameters, speckle_data) 
    #ProductIO.writeProduct(calib_data, calib_file, 'BEAM-DIMAP')
    print('---end of calibration---')
        
    ### TERRAIN CORRECTION - EW Full 200 m
    parameters = HashMap()    
    parameters.put('demName', 'ACE2_5Min')
    parameters.put('externalDEMNoDataValue', 0.0)
    parameters.put('demResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('imgResamplingMethod', "BILINEAR_INTERPOLATION")
    parameters.put('pixelSpacingInMeter', 200.0)
    parameters.put('pixelSpacingInDegree', 0.001796630568239043)
    parameters.put('mapProjection', "EPSG:32634")    #WGS 84 / UTM zone 34N (Spatial Reference)
    
    terrain_data_200m = GPF.createProduct('Terrain-Correction', parameters,  calib_data)
    print('---end of terrain---')
    
    ### SUBSET
    WKTReader = snappy.jpy.get_type('com.vividsolutions.jts.io.WKTReader')
    wkt = "POLYGON((15 80, 35 80, \
                    35 82.5, 15 82.5, \
                    15 80))"
  
                        
    geom = WKTReader().read(wkt)
 
    subsettings = HashMap()
    subsettings.put('geoRegion', geom)
    subsettings.put('outputImageScaleInDb', False)
 
    subset_file_200m = out_path_lowres + file1 + polarization + "_terrian_200m_subset" 
    
    #print(subset_file_40m)
    subset_data_200m = GPF.createProduct("Subset", subsettings, terrain_data_200m)
    ProductIO.writeProduct(subset_data_200m, subset_file_200m, 'GeoTiff')
    print('---end of subset---')
