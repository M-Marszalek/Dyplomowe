import numpy as np
import random as rn
import pulp as pu
import folium
import osrm
import geocoder
from folium import plugins
import time
import csv

def replace_coord(place):
    replaced = []
    replaced.append(place[1])
    replaced.append(place[0])
    return (replaced)

def get_distance(resp1):
    resp2 = resp1['routes']
    resp3 = resp2[0]
    resp4 = resp3['legs']
    resp5 = resp4[0]
    return resp5['distance']

def get_coordinats(adreses):
    coordinats = []
    for i in range(adreses.shape[0]):
        place = geocoder.osm(adreses[i])
        coordinats.append(place.latlng)
    return np.array(coordinats)

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

def replace_coll(db):
    dbd = db
    for rows in range(db.shape[0]):
        a = db[rows, 1]
        db[rows, 1] = db[rows, 0]
        db[rows, 0] = a
    print(dbd, db)
    return db

def sum_coll(base, col_no):
    sumc = 0
    for k in range(len(base[:, 0])):
        sumc += (base[1, col_no])
    return sumc

def distance_matrix(faci, cost):
    step = 0
    fullmatrix = faci.shape[0]*cost.shape[0]
    print(fullmatrix)
    dist = np.zeros((faci.shape[0], cost.shape[0]))
    for c in range(cost.shape[0]):
        for f in range(faci.shape[0]):
            response = client.route(
            coordinates=[faci[f, :], cost[c, :]])
            dist[f, c] = get_distance(response)/1000
            globals()['trip%s' % (str(f)+str(c))] = route_coords(response)
            step += 1
            print(step)
    return dist


def dataset(cos):
    adress = cos[:, :1]
    placeprop = cos[:, 1:]
    placeprop = placeprop.astype('float')
    return adress, placeprop

print('Hello world')
start_time = time.time()

client = osrm.Client(host='http://router.project-osrm.org', profile='car')

with open("TestCosL.csv", "r", newline='') as csvfile1:
    readercos = list(csv.reader(csvfile1, delimiter='|'))
readercos = np.array(readercos)
cosadress, cosdata = dataset(readercos)

with open("TestFacL.csv", "r", newline='') as csvfile1:
    readerfac = list(csv.reader(csvfile1, delimiter='|'))
readerfac = np.array(readerfac)
facadress, facdata = dataset(readerfac)

u = np.array(facdata[:, 0])
f = np.array(facdata[:, 1])
d = np.array(cosdata[:, 0])
print(u,f,d)
# sum of demand/supply

supp = sum_coll(facdata, 0)
dem = sum_coll(cosdata, 0)
print("popyt:", dem)
print("podaż:", supp)
if dem>supp:
    print("brak optymalnego rozwiązania")
else:
    print("istnieje optymalne rozwiazanie")

facadress = get_coordinats(facadress)
cosadress = get_coordinats(cosadress)

facility = np.hstack((facadress, facdata))
costumers = np.hstack((cosadress, cosdata))

print(facility, costumers)
# cost

data_map = folium.Map([51.1380, 16.7294], zoom_start=8)

for i in range(facility.shape[0]):
     folium.Marker((facility[i, 0], facility[i,1]),
        popup=('magazyn %i produkuje %i jednostek towaru,\n koszt utrzymania to: %i' %(i, int(facility[i, 2]), facility[i, 3])),
        icon=folium.Icon(color='cadetblue')).add_to(data_map)
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :2]),
        popup=('klient %i potrzebuje %i jednostek towaru' %(i, int(d[i]))),
        icon=folium.Icon(color='blue')).add_to(data_map)
data_map.save('Data.html')

facadress = replace_coll(facadress)
cosadress = replace_coll(cosadress)

distance = distance_matrix(facadress, cosadress)
print(distance)

# solver

problem = pu.LpProblem("FacLoc", pu.LpMinimize)

# zmienne dec

y = pu.LpVariable.dicts("y",
                        [(i, j) for i in range(facility.shape[0])
                        for j in range(costumers.shape[0])], 0, 1, pu.LpBinary)
x = pu.LpVariable.dicts("x", range(facility.shape[0]), 0, 1, pu.LpBinary)

# funkcja


problem += (pu.lpSum(f[i] * x[i] for i in range(facility.shape[0]))
            + pu.lpSum(distance[i, j] * y[i, j] * d[j] for i in range(facility.shape[0]) for j in range(costumers.shape[0])))

# ograniczenia

for j in range(costumers.shape[0]):
    problem += pu.lpSum(y[(i, j)] for i in range(facility.shape[0])) == 1

for i in range(facility.shape[0]):
    problem += (pu.lpSum(y[(i, j)] * d[(j)] for j in range(costumers.shape[0])) <= x[i] * u[i])


problem.solve()

print("status: ", pu.LpStatus[problem.status])

fac_cos = []
ya = np.zeros(np.shape(distance))
xa = np.zeros(facility.shape[0])
for i in range(facility.shape[0]):
    xa[i] = x[i].varValue
    globals()['facility%s' % i] = 'Magazyn ' + str(i) + ' obsługuje klientów: '
    for j in range(costumers.shape[0]):

        ya[i, j] = y[i, j].varValue
        if ya[i, j] > 0:
            globals()['facility%s' % i] += str(j)+', '
            globals()['costumer%s' % j] = 'klient ' + str(j) + ' jest obsługiwany przez magazyn: '+ str(i)
            fac_cos.append([i,j])
    globals()['facility%s' % i] = globals()['facility%s' % i][:-2]

fac_cos = np.array(fac_cos)
print(xa, "\n", ya)
print(fac_cos)


great = []
bad = []
lpg = []
lpb = []
for lp in range(facility.shape[0]):
    if xa[lp] > 0:
        great.append([facility[lp, 0], facility[lp, 1]])
        lpg.append(lp)
    else:
        bad.append([facility[lp, 0], facility[lp, 1]])
        lpb.append(lp)

great = (np.array(great))
bad = (np.array(bad))


print(great, '\nclosed:\n', bad)

solve_map = folium.Map([51.1380, 16.7294], zoom_start=8)

for i in range(great.shape[0]):
     folium.Marker((great[i, :]), popup=globals()['facility%s' % lpg[i]],
                   icon=folium.Icon(color='green')).add_to(solve_map)
for i in range(bad.shape[0]):
     folium.Marker((bad[i, :]), popup='Magazyn %i jest zamkniety' % lpb[i],
                   icon=folium.Icon(color='red')).add_to(solve_map)
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :2]), popup= globals()['costumer%s' % i],
                   icon=folium.Icon(color='blue')).add_to(solve_map)
for i in range(fac_cos.shape[0]):
    tripid = str(fac_cos[i, 0])+str(fac_cos[i, 1])
    print(tripid)
    plugins.AntPath(globals()['trip%s' % tripid], color='blue').add_to(solve_map)

solve_map.save('Solve.html')

print("--- %s seconds ---" % (time.time() - start_time))
print("fajnie było")
