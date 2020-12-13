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

def get_coordinats(adreses, back):
    coordinats = []
    for i in range(adreses.shape[0]):
        msc = None
        cor = 0
        while msc == None:
            place = geocoder.osm(adreses[i])
            msc = place.latlng
            cor = cor + 1
            if cor > 3:
                print("użyto zastępczych koordynatów, miejsce %i" % i)
                msc = [back[i][0], back[i][1]]
        coordinats.append(msc)
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
    placeprop = cos[:, 1:-2]
    backup = cos[:, -2:]
    placeprop = placeprop.astype('float')
    backup = backup.astype('float')
    return adress, placeprop, backup


while True:
    try:
        set = int(input("Wybierz zestaw danych 1, 2 lub 3: "))
    except ValueError:
        print("Podaj numer zestawu danych, który chcesz wybrać.")
        continue
    if set not in (1, 2, 3):
        print("Podaj numer zestawu danych, który chcesz wybrać.")
        continue
    else:
        break

set = set-1
DataSets = [["Test\TestCosS.csv", "Test\TestFacS.csv", 'Test\DataS_MediaMarkt.html', 'Test/SolveS_MediaMarkt.html', "odp.csv"],
           ["Test\TestCosM.csv", "Test\TestFacM.csv", 'Test\DataM_Jysk.html', 'Test/SolveM_Jysk.html', "odp1.csv"],
           ["Test\TestCosL.csv", "Test\TestFacL.csv", 'Test\DataL_Lidl.html', 'Test/SolveL_Lidl.html.html', "odp2.csv"]]

start_time = time.time()

client = osrm.Client(host='http://router.project-osrm.org', profile='car')

with open(DataSets[set][0], "r", newline='') as csvfile1:
    readercos = list(csv.reader(csvfile1, delimiter='|'))
readercos = np.array(readercos)
cosadress, cosdata, cosback = dataset(readercos)


with open(DataSets[set][1], "r", newline='') as csvfile1:
    readerfac = list(csv.reader(csvfile1, delimiter='|'))
readerfac = np.array(readerfac)
facadress, facdata, facback = dataset(readerfac)


facadress = get_coordinats(facadress, facback)
cosadress = get_coordinats(cosadress, cosback)


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

group0 = folium.FeatureGroup(name='<span style="color: navy">Magazyny</span>')
for i in range(facility.shape[0]):
     folium.Marker((facility[i, 0], facility[i,1]),
        popup=('magazyn %i produkuje %i jednostek towaru,\n koszt utrzymania to: %i' %(i+1, int(facility[i, 2]), facility[i, 3])),
        icon=folium.Icon(color='cadetblue')).add_to(group0)
group0.add_to(data_map)

group1 = folium.FeatureGroup(name='<span style="color: blue">Punkty dystrybucji</span>')
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :2]),
        popup=('punkt dystrybucji %i potrzebuje %i jednostek towaru' %(i+1, int(costumers[i, 2]))),
        icon=folium.Icon(color='blue')).add_to(group1)
group1.add_to(data_map)
folium.map.LayerControl('topright', collapsed=False).add_to(data_map)
data_map.save(DataSets[set][2])

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

group2 = folium.FeatureGroup(name='<span style="color: lime">Otwarte magazyny</span>')
for i in range(good.shape[0]):
     folium.Marker((good[i, :]), popup=globals()['facility%s' % lpg[i]],
                   icon=folium.Icon(color='green')).add_to(group2)
group2.add_to(solve_map)
group3 = folium.FeatureGroup(name='<span style="color: red">Zamknięte magazyny</span>')
for i in range(bad.shape[0]):
     folium.Marker((bad[i, :]), popup='Magazyn %i jest zamkniety' % lpb[i],
                   icon=folium.Icon(color='red')).add_to(group3)
group3.add_to(solve_map)
group4 = folium.FeatureGroup(name='<span style="color: blue">Punkty dystrybucji</span>')
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :2]), popup= globals()['costumer%s' % i],
                   icon=folium.Icon(color='blue')).add_to(group4)
group4.add_to(solve_map)

for i in range(fac_cos.shape[0]):
    tripid = str(fac_cos[i, 0])+str(fac_cos[i, 1])
    print(tripid)
    plugins.AntPath(globals()['trip%s' % tripid], color='blue').add_to(solve_map)

folium.map.LayerControl('topright', collapsed=False).add_to(solve_map)
solve_map.save(DataSets[set][3])

save = []
for i in range(good.shape[0]):
    save.append([globals()['facility%s' % lpg[i]]])
for i in range(bad.shape[0]):
    save.append(['Magazyn %i jest zamkniety' % (lpb[i]+1)])

print(save)
print(np.array(save))

with open(DataSets[set][4], "w",  newline='') as f:
    writer = csv.writer(f,  delimiter='|')
    writer.writerows(save)


print("Wartość funkcji celu jest równa %.2f PLN/miesiecznie" % pu.value(problem.objective) )


