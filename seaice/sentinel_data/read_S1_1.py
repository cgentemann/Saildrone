
file1 = 'S1A_EW_GRDM_1SDH_20170601T053330_20170601T053435_016836_01BFD7_A0B2.zip'

import os.path
import snappy
from snappy import ProductIO
from snappy import Product
from snappy import ProductData
from snappy import ProductUtils

jpy = snappy.jpy

if os.path.exists(file1):
    # Read sourceProduct and get information needed to create target product:
    sourceProduct = snappy.ProductIO.readProduct(file1)
    width = sourceProduct.getSceneRasterWidth()
    height = sourceProduct.getSceneRasterHeight()

    #Create target product:
    targetProduct = Product('FLH_Product', 'FLH_Type', width, height)
    targetBand = targetProduct.addBand('FLH', ProductData.TYPE_FLOAT32)
    ProductUtils.copyGeoCoding(sourceProduct, targetProduct)
    targetProduct.setProductWriter(ProductIO.getProductWriter('GeoTIFF'))

    # Use calibration operator - I've taken "org.esa.s1tbx.calibration.gpf.CalibrationOp" from the help window
    CalibrationOp = jpy.get_type("org.esa.s1tbx.calibration.gpf.CalibrationOp")
    CalOp = CalibrationOp()
    CalOp = CalibrationOp()
    CalOp.setSourceProduct(sourceProduct)
    CalOp.setParameter('doSomethng', True)

    targetProduct = CalOp.getTargetProduct()
    snappy.ProductIO.writeProduct(targetProduct, 'toFile.dim', 'BEAM-DIMAP')

    #### HERE I DO NOT KNOW HOW TO EXECUTE this operator
    #### When I try to execute: 'doExecute' or 'execute' methods, I receive an error message
    ### targetProduct.closeIO()

