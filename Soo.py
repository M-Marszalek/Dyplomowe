import matplotlib.pyplot as mpl
import numpy as np
import random as rn
import math as mt
import pulp as pu

dim = [0, 200]
ware_no = 17
sto_no = 40


def sum_coll(base, col_no):
    sumc = 0
    for k in range(len(base[:, 0])):
        sumc += base[1, col_no]
    return sumc


def dist_o_meter(ware, sto):
    dist = np.zeros((sto_no, ware_no))
    for s in range(len(sto[:, 0])):
        for w in range(len(ware[:, 0])):
            dist[s, w] = mt.sqrt(pow(ware[w, 0] - sto[s, 0], 2) + pow(ware[w, 1] - sto[s, 1], 2))
    return dist


print('Hello world')

warehouses = []
for i in range(ware_no):
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    u1 = rn.randint(20, 40) * 100
    f1 = rn.randint(10000, 30000)
    new_ware = ([xlab, ylab, u1, f1])
    warehouses.append(new_ware)
warehouses = np.array(warehouses)

u = warehouses[:, 2]
f = warehouses[:, 3]

stores = []
for i in range(sto_no):
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    d1 = rn.randint(20, 40) * 25
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

# cost
distance = dist_o_meter(warehouses, stores)
distance = np.transpose(distance)
print("\nodległosci: \n", distance)


mpl.figure(1)
mpl.plot(warehouses[:, 0], warehouses[:, 1], 'ro')
mpl.plot(stores[:, 0], stores[:, 1], 'bo')
mpl.axis([dim[0], dim[1], dim[0], dim[1]])
mpl.show()

# solver

problem = pu.LpProblem("FacLoc", pu.LpMinimize)

# zmienne dec

y = pu.LpVariable.dicts("y",
                        [(i, j) for i in range(ware_no)
                        for j in range(sto_no)], 0, 1, pu.LpBinary)
x = pu.LpVariable.dicts("x", range(ware_no), 0, 1, pu.LpBinary)

# funkcja


problem += (pu.lpSum(f[i] * x[i] for i in range(ware_no))
            + pu.lpSum(distance[i, j] * y[i, j] * d[j] for i in range(ware_no) for j in range(sto_no)))

# ograniczenia

for j in range(sto_no):
    problem += pu.lpSum(y[(i, j)] for i in range(ware_no)) == 1

for i in range(ware_no):
    problem += (pu.lpSum(y[(i, j)] * d[(j)] for j in range(sto_no)) <= x[i] * u[i])


problem.solve()

print("status: ", pu.LpStatus[problem.status])

ya = np.zeros(np.shape(distance))
xa = np.zeros(ware_no)
for i in range(ware_no):
    xa[i] = x[i].varValue
    for j in range(sto_no):
        ya[i, j] = y[i, j].varValue

print(xa, "\n", ya)

great = []
bad = []
for lp in range(ware_no):
    if xa[lp] > 0:
        great.append([warehouses[lp, 0], warehouses[lp, 1]])
    else:
        bad.append([warehouses[lp, 0], warehouses[lp, 1]])

great = np.array(great)
bad = np.array(bad)

print(great, '\nclosed:\n', bad)

# tworzenie polaczen
conn = []
for i in range(ware_no):
    for j in range(sto_no):
        if ya[i, j] > 0:
            conn.append([warehouses[i, 0], warehouses[i, 1], stores[j, 0], stores[j, 1]])
conn = np.array(conn)
print(conn)

mpl.figure(2)

for l in range(conn.shape[0]):
    mpl.plot([conn[l, 0], conn[l, 2]], [conn[l, 1], conn[l, 3]], 'g')
mpl.plot(great[:, 0], great[:, 1], 'yo')
mpl.plot(bad[:, 0], bad[:, 1], 'rs')
mpl.plot(stores[:, 0], stores[:, 1], 'bo')
mpl.axis([dim[0], dim[1], dim[0], dim[1]])
mpl.show()

print("fajnie było")
