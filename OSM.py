
import folium
from folium import plugins
import numpy as np
import osrm
import geocoder

def replace_coord(place):
     replaced = []
     replaced.append(place[1])
     replaced.append(place[0])
     return(replaced)

def replace_coll(db):
     dbd = np.zeros(db.shape)
     for rows in range(db.shape[0]):
         dbd[rows, 0] = db[rows, 1]
         dbd[rows, 1] = db[rows, 0]
     return dbd

def get_coordinats(adreses):
    for i in range(adreses.shape[0]):


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

def get_fac():
     fac= []
     while True:
          adress = input('podaj adres: ')
          adress = geocoder.osm(adress)
          if not adress:
               print("Nie mogę znaleźć podanego adresu. Spróbuj jeszcze raz")
               continue
          else:
               break
     return adress.latlng

def get_costum():
     while True:
          start = input('podaj adres: ')
          start = geocoder.osm(start)
          if not start:
               print("Nie mogę znaleźć podanego adresu. Spróbuj jeszcze raz")
               continue
          else:
               break
     return start.latlng




pocz= replace_coord(get_fac())
fini = replace_coord(get_costum())


place = geocoder.osm("Kino nowe horyzonty")


print(place.latlng)


coords = place.latlng
print(type(coords[0]))

client = osrm.Client(host='http://router.project-osrm.org', profile='car')

response = client.route(
     coordinates=[pocz, fini])


print(get_distance(response)/1000,'km')
print(response)



trip = route_coords(response)

m = folium.Map([51.1380, 16.7294], zoom_start=9)
folium.Marker(replace_coord(pocz
               )).add_to(m)
folium.Marker(replace_coord(fini)).add_to(m)
folium.Marker(coords, popup='TO TU', icon=folium.Icon(color='red')).add_to(m)
folium.plugins.AntPath(trip).add_to(m)
m.save('BETA.html')


