import gdal
import folium
from folium import raster_layers
from folium import features
import urllib.request

starttime='2019-06-14'
endtime='2019-06-14'
url = 'https://services.sentinel-hub.com/ogc/wms/5887863d-3c49-4c96-8c62-afc13dd8a04a?SERVICE=WMS&REQUEST=GetMap&SHOWLOGO=true&MAXCC=100&TIME='+starttime+'%2F'+endtime+'&CRS=EPSG%3A4326&FORMAT=image%2Ftiff%3Bdepth%3D8&BBOX=73.00556612657772%2C-150.41441917419436%2C67.9197529862965%2C-182.05504417419436&evalscriptoverrides=&LAYERS=EW-DH-HH-DECIBEL-GAMMA0-ORTHORECTIFIED&WIDTH=2752&HEIGHT=1330&NICENAME=S1.tiff&COVERAGE' 
urllib.request.urlretrieve(url,'S11.tiff')  
    
#If you want 3857 format, just change the link into
#https://services.sentinel-hub.com/ogc/wms/5887863d-3c49-4c96-8c62-afc13dd8a04a?SERVICE=WMS&REQUEST=GetMap&SHOWLOGO=true&MAXCC=100&TIME=2019-06-14%2F2019-06-14&CRS=EPSG%3A3857&FORMAT=image%2Fpng&BBOX=-20205487%2C10411576%2C-16682927%2C12108856&evalscriptoverrides=&LAYERS=EW-DH-HH-DECIBEL-GAMMA0-ORTHORECTIFIED&WIDTH=2752&HEIGHT=1326&NICENAME=Sentinel-1+AWS+%28S1-AWS-EW-HHHV%29+from+2019-06-14.png&TRANSPARENT=0&BGCOLOR=00000000

#Open S1 ice file
driver=gdal.GetDriverByName('GTiff')
driver.Register() 
ds = gdal.Open('S1.tiff') 
if ds is None:
    print('Could not open the Copernicus Sentinel-1 ice data')

geotransform = ds.GetGeoTransform()
cols = ds.RasterXSize 
rows = ds.RasterYSize 
xmin=geotransform[0]
ymax=geotransform[3]
xmax=xmin+cols*geotransform[1]
ymin=ymax+rows*geotransform[5]
centerx=(xmin+xmax)/2
centery=(ymin+ymax)/2

#Raster convert to array in numpy
bands = ds.RasterCount
band=ds.GetRasterBand(1)
dataimage= band.ReadAsArray(0,0,cols,rows)


#Visualization in folium
map= folium.Map(location=[centery, centerx], zoom_start=7,tiles='Stamen Terrain')
raster_layers.ImageOverlay(
    image=dataimage,
    bounds=[[ymin, xmin], [ymax, xmax]],
    colormap=lambda x: (0, 0, 0, x),#R,G,B,alpha
    #if I want white background then R,G,B is 1,1,1 
).add_to(map)

saildrone_path= folium.PolyLine(locations=[[68,-168],[69,1-164],[71,-162],[72,-156]],color='red') #assume the path of Saildrone
saildrone_path.add_to(map) #put the path into map


startplot = features.Marker([68,-168])
startplotpp = folium.Popup('saildrone_start')
startplotic = features.Icon(color='red')
startplot.add_child(startplotic)
startplot.add_child(startplotpp)
map.add_child(startplot)

endplot = features.Marker([72,-156])
endplotpp = folium.Popup('saildrone_end')
endplotic = features.Icon(color='blue')
endplot.add_child(endplotic)
endplot.add_child(endplotpp)
map.add_child(endplot)

#Save the final plot
map.save('C:/Users/gentemann/Google Drive/public/saildrone/seaice_with_saildronepath.html')