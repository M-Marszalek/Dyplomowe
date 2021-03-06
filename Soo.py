import numpy as np
import random as rn
import pulp as pu
import folium
import osrm
import geocoder
from folium import plugins
import time



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
        sumc += base[1, col_no]
    return sumc

def distance_matrix(faci, cost):
    dist = np.zeros((faci.shape[0], cost.shape[0]))
    for c in range(cost.shape[0]):
        for f in range(faci.shape[0]):
            response = client.route(
            coordinates=[[faci[f, 0], faci[f, 1]], cost[c,:]])
            dist[f, c] = get_distance(response)/1000
            globals()['trip%s' % (str(f)+str(c))] = route_coords(response)
    return dist


def get_fac(numadr):
    while True:
        adresses = ['wrocław', 'wałbrzych', 'Legnica', 'bolesławiec', 'ząbkowice śląskie ']
        adress = adresses[numadr]
        adress = geocoder.osm(adress)
        if not adress:
            print("Nie mogę znaleźć podanego adresu. Spróbuj jeszcze raz")
            continue
        else:
            break
    fac = adress.latlng
    fac.append(rn.randint(20, 40) * 100)
    fac.append(rn.randint(65000, 80000))
    return fac



print('Hello world')
start_time = time.time()

client = osrm.Client(host='http://router.project-osrm.org', profile='car')
facility = []
for i in range(5):
    facility.append(get_fac(i))

facility = replace_coll(np.array(facility))


costumers = np.array([[16.6031, 51.1621],
            [15.5786, 51.2533],
            [16.636,  50.44],
            [17.1057, 50.7782],
            [16.8997, 51.4557],
            [16.5619, 51.6589],
            [16.1115, 50.9117],
            [16.441,  51.3992],
            [15.3946, 50.9636],
            [16.5042, 50.8285]])


u = facility[:, 2]
f = facility[:, 3]

stores = []
for i in range(costumers.shape[0]):
    xlab = costumers[i, 0]
    ylab = costumers[i, 1]
    d1 = rn.randint(20, 30) * 25
    new_sto = ([xlab, ylab, d1])
    stores.append(new_sto)
stores = np.array(stores)

d = stores[:, 2]

print("magazyny: \n", facility)
print("sklepy: \n", stores)

# sum of demand/supply

supp = sum_coll(facility, 2)
dem = sum_coll(stores, 2)
print("popyt:", dem)
print("podaż:", supp)
if dem>supp:
    print("brak optymalnego rozwiązania")
else:
    print("istnieje optymalne rozwiazanie")

distance = distance_matrix(facility, costumers)

print(distance)
# cost

#distance = np.transpose(distance)
#print("\nodległosci: \n", distance)

facility = replace_coll(facility)
costumers = replace_coll(costumers)

data_map = folium.Map([51.1380, 16.7294], zoom_start=8)

for i in range(facility.shape[0]):
     folium.Marker((facility[i, 0], facility[i,1]),
        popup=('magazyn %i produkuje %i jednostek towaru,\n koszt utrzymania to: %i' %(i, int(facility[i, 2]), facility[i, 3])),
        icon=folium.Icon(color='cadetblue')).add_to(data_map)
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :]),
        popup=('klient ' + str(i) + ' potrzebuje ' + str(int(stores[i, 2])) + ' jednostek towaru'),
        icon=folium.Icon(color='blue')).add_to(data_map)
data_map.save('Data.html')

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
     folium.Marker((costumers[i, :]), popup= globals()['costumer%s' % i],
                   icon=folium.Icon(color='blue')).add_to(solve_map)
for i in range(fac_cos.shape[0]):
    tripid = str(fac_cos[i, 0])+str(fac_cos[i, 1])
    print(tripid)
    plugins.AntPath(globals()['trip%s' % tripid], color='blue').add_to(solve_map)

solve_map.save('Solve.html')

print("--- %s seconds ---" % (time.time() - start_time))
print("fajnie było")
