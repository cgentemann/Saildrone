
#Python34

import os
import folium

print(folium.__version__)

from folium import plugins

path = 'D:/Project_Data/Arctic_PRIZE/Processed_Data/S1'

merc = os.path.join(path, 'S1A_EW_GRDM_1SDH_20170601T071215_20170601T071320_016837_01BFE1_35BF_terrian_200mHH.tif')

m = folium.Map([37, 0], zoom_start=1, tiles='stamentoner')

img = plugins.ImageOverlay(
    name='Mercator projection SW',
    image=merc,
    bounds=[[15, 80], [83, 35]],
    opacity=0.6,
    interactive=True,
    cross_origin=False,
    zindex=1,
)


folium.Popup('I am an image').add_to(img)

img.add_to(m)

folium.LayerControl().add_to(m)

m.save(os.path.join('results', 'ImageOverlay_0.html'))

m
