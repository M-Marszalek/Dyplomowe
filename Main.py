import matplotlib.pyplot as mpl
import numpy as np
import random as rn
import math as mt
import pulp as pu
import folium
from folium import plugins
import osrm


def replace_coord(place):
    replaced = []
    replaced.append(place[1])
    replaced.append(place[0])
    return (replaced)


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

def replace_coll(db):
    dbd = np.zeros(db.shape)
    for rows in range(db.shape[0]):
        dbd[rows, 0] = db[rows, 1]
        dbd[rows, 1] = db[rows, 0]

    return dbd

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
            coordinates=[faci[f,:], cost[c,:]])
            dist[f, c] = get_distance(response)/1000
    return dist



print('Hello world')

client = osrm.Client(host='http://router.project-osrm.org', profile='car')

facility = np.array([[16.0812, 51.1759],
            [16.2666, 50.7365],
            [17.0068, 51.0423],
            [15.760, 50.924],
            [17.0432, 51.3173]])
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


warehouses = []
for i in range(facility.shape[0]):
    xlab = facility[i, 0]
    ylab = facility[i, 1]
    u1 = rn.randint(30, 40) * 100
    f1 = rn.randint(10000, 30000)
    new_ware = ([xlab, ylab, u1, f1])
    warehouses.append(new_ware)
warehouses = np.array(warehouses)

u = warehouses[:, 2]
f = warehouses[:, 3]

stores = []
for i in range(costumers.shape[0]):
    xlab = costumers[i, 0]
    ylab = costumers[i, 1]
    d1 = rn.randint(20, 30) * 25
    new_sto = ([xlab, ylab, d1])
    stores.append(new_sto)
stores = np.array(stores)

d = stores[:, 2]

print("magazyny: \n", warehouses)
print("sklepy: \n", stores)

# sum of demand/supply

supp = sum_coll(warehouses, 2)
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
     folium.Marker((facility[i, :]), popup=i, icon=folium.Icon(color='yellow')).add_to(data_map)
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :]), popup=i, icon=folium.Icon(color='blue')).add_to(data_map)
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

ya = np.zeros(np.shape(distance))
xa = np.zeros(facility.shape[0])
for i in range(facility.shape[0]):
    xa[i] = x[i].varValue
    for j in range(costumers.shape[0]):
        ya[i, j] = y[i, j].varValue

print(xa, "\n", ya)

great = []
bad = []
for lp in range(facility.shape[0]):
    if xa[lp] > 0:
        great.append([warehouses[lp, 0], warehouses[lp, 1]])
    else:
        bad.append([warehouses[lp, 0], warehouses[lp, 1]])

great = replace_coll(np.array(great))
bad = replace_coll(np.array(bad))


print(great, '\nclosed:\n', bad)

solve_map = folium.Map([51.1380, 16.7294], zoom_start=8)

for i in range(great.shape[0]):
     folium.Marker((great[i, :]), popup='open', icon=folium.Icon(color='green')).add_to(solve_map)
for i in range(bad.shape[0]):
     folium.Marker((bad[i, :]), popup='closed', icon=folium.Icon(color='purple')).add_to(solve_map)
for i in range(costumers.shape[0]):
     folium.Marker((costumers[i, :]), icon=folium.Icon(color='blue')).add_to(solve_map)

solve_map.save('Solve.html')

print("fajnie było")
