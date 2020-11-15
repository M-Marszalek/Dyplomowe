import folium
from folium import plugins
import pandas as pd
import matplotlib.pyplot as plt
from IPython.core.display import display, HTML
import IPython.display as ipyd
import osrm_plus
import requests
import polyline
import numpy as np
import osrm

def replace_coord(place):
     replaced = []
     replaced.append(place[1])
     replaced.append(place[0])
     return(replaced)

def get_distance(resp):
     resp2 = resp['routes']
     resp3 = resp2[0]
     resp4 = resp3['legs']
     resp5 = resp4[0]
     return resp5['distance']

def route_coords(resp1):
     resp2 = resp1['routes']
     resp3 = resp2[0]
     resp4 = (resp3['geometry'])['coordinates']
     resp5 = np.array(resp4)
     a = np.zeros(resp5.shape)
     for i in range(resp5.shape[0]):
          a[i, 0] = resp5[i, 1]
          a[i, 1] = resp5[i, 0]
     return a

dom = [16.48642, 50.84236]
pwr = [17.0618875, 51.1075006]



client = osrm.Client(host='http://router.project-osrm.org', profile='car')


response = client.route(
     coordinates=[pwr, dom])


print(get_distance(response)/100,'km')
print(response)

trip = route_coords(response)

m = folium.Map([51.1380, 16.7294], zoom_start=9)
folium.Marker(replace_coord(pwr)).add_to(m)
folium.Marker(replace_coord(dom)).add_to(m)
for i in range(trip.shape[0]):
     folium.Marker(([trip[i, 0], trip[i, 1]]), popup=i, icon=folium.Icon(color='red')).add_to(m)
folium.plugins.AntPath(trip).add_to(m)
m.save('DWR.html')
ipyd.IFrame('DWR.html', width=1000, height=500)

