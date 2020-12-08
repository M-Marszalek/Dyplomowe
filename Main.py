import numpy as np
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
        msc = None
        while msc == None:
            place = geocoder.osm(adreses[i])
            msc = place.latlng
            print(adreses[i], msc)
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

def sum_col(base, col_no):
    sumc = 0
    for k in range(len(base[:, 0])):
        sumc += (base[1, col_no])
    return sumc

def replace_col(db):
    dbd = db
    for rows in range(db.shape[0]):
        a = db[rows, 1]
        db[rows, 1] = db[rows, 0]
        db[rows, 0] = a
    print(dbd, db)
    return db

def distance_matrix(faci, cost):
    step = 0
    fullmatrix = faci.shape[0]*cost.shape[0]
    dist = np.zeros((faci.shape[0], cost.shape[0]))
    for c in range(cost.shape[0]):
        for f in range(faci.shape[0]):
            response = client.route(
            coordinates=[faci[f, :], cost[c, :]])
            dist[f, c] = get_distance(response)/1000
            globals()['trip%s' % (str(f)+str(c))] = route_coords(response)
            step += 1
            print('%.2f' % ((step/fullmatrix)* 100) + " %")
    return dist

def set_center(places):
    lat = places[:, 0]
    lng = places[:, 1]
    minlat = min(lat)
    minlng = min(lng)
    maxlat = max(lat)
    maxlng = max(lng)
    #size = abs(maxlat - minlat) * abs(maxlng - minlng)
    return [((minlat+maxlat)/2), ((minlng+maxlng)/2)]

def dataset(cos):
    adress = cos[:, :1]
    placeprop = cos[:, 1:]
    placeprop = placeprop.astype('float')
    return adress, placeprop

start_time = time.time()

client = osrm.Client(host='http://router.project-osrm.org', profile='car')

with open("Test\TestCosL.csv", "r", newline='') as csvfile1:
    readercos = list(csv.reader(csvfile1, delimiter='|'))
readercos = np.array(readercos)
cosadress, cosdata = dataset(readercos)

with open("Test\TestFacL.csv", "r", newline='') as csvfile1:
    readerfac = list(csv.reader(csvfile1, delimiter='|'))
readerfac = np.array(readerfac)
facadress, facdata = dataset(readerfac)

cosadress = get_coordinats(cosadress)
facadress = get_coordinats(facadress)

# sum of demand/supply
supp = sum_col(facdata, 0)
dem = sum_col(cosdata, 0)
if dem>supp:
    print("brak optymalnego rozwiązania")
    exit(0)
else:
    print("istnieje optymalne rozwiązanie")

facility = np.hstack((facadress, facdata))
costumers = np.hstack((cosadress, cosdata))

center = set_center(np.vstack((cosadress, facadress)))

data_map = folium.Map(center, zoom_start=8)

for i in range(facility.shape[0]):
     folium.Marker((facility[i, 0], facility[i,1]),
        popup=('magazyn %i produkuje %i jednostek towaru,\n koszt utrzymania to: %i' %(i, int(facility[i, 2]), facility[i, 3])),
        icon=folium.Icon(color='cadetblue')).add_to(data_map)
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :2]),
        popup=('punkt dystrybucji %i potrzebuje %i jednostek towaru' %(i, int(costumers[i, 2]))),
        icon=folium.Icon(color='blue')).add_to(data_map)
data_map.save('Test\DataL_Lidl.html')

facadress = replace_col(facadress)
cosadress = replace_col(cosadress)

distance = distance_matrix(facadress, cosadress)

u = np.array(facdata[:, 0])
f = np.array(facdata[:, 1])
d = np.array(cosdata[:, 0])

# solver

problem = pu.LpProblem("FacLoc", pu.LpMinimize)

# zmienne decyzyjne

y = pu.LpVariable.dicts("y",
                        [(i, j) for i in range(facility.shape[0])
                        for j in range(costumers.shape[0])], 0, 1, pu.LpBinary)
x = pu.LpVariable.dicts("x", range(facility.shape[0]), 0, 1, pu.LpBinary)

# funkcja celu


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
    globals()['facility%s' % i] = 'Magazyn ' + str(i+1) + ' obsługuje punkty dystrybucji: '
    for j in range(costumers.shape[0]):
        ya[i, j] = y[i, j].varValue
        if ya[i, j] > 0:
            globals()['facility%s' % i] += str(j+1)+', '
            globals()['costumer%s' % j] = 'punkt dystrybucji ' + str(j) + ' jest obsługiwany przez magazyn: '+ str(i)
            fac_cos.append([i,j])
    globals()['facility%s' % i] = globals()['facility%s' % i][:-2]
fac_cos = np.array(fac_cos)

print(xa, "\n", ya)
print(fac_cos)

good = []
bad = []
lpg = []
lpb = []
for lp in range(facility.shape[0]):
    if xa[lp] > 0:
        good.append([facility[lp, 0], facility[lp, 1]])
        lpg.append(lp)
    else:
        bad.append([facility[lp, 0], facility[lp, 1]])
        lpb.append(lp)
good = (np.array(good))
bad = (np.array(bad))


print(good, '\nclosed:\n', bad)

solve_map = folium.Map(center, zoom_start=8)

for i in range(good.shape[0]):
     folium.Marker((good[i, :]), popup=globals()['facility%s' % lpg[i]],
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

save = []
for i in range(good.shape[0]):
    save.append([globals()['facility%s' % lpg[i]]])
for i in range(bad.shape[0]):
    save.append(['Magazyn %i jest zamkniety' % (lpb[i]+1)])

print(save)
print(np.array(save))

with open("odp2.csv", "w",  newline='') as f:
    writer = csv.writer(f,  delimiter='|')
    writer.writerows(save)

solve_map.save('Test/SolveL_Lidl.html')

print(pu.value(problem.objective))

print("--- %s seconds ---" % (time.time() - start_time))
print("fajnie było")
