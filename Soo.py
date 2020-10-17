import matplotlib.pyplot as mpl
import numpy as np
import random as rn
import math as mt
import pulp as pu

dim = [0, 100]
ware_no = 5
sto_no = 12


def sum_coll(base, col_no):
    sumc = 0
    for k in range(len(base[:, 0])):
        sumc += base[1, col_no]
    return sumc


def dist_o_meter(ware, sto):
    dist = np.zeros((sto_no, ware_no))
    for s in range(len(sto[:, 0])):
        for w in range(len(ware[:, 0])):
            dist[s, w] = mt.sqrt(pow(ware[w, 1] - sto[s, 1], 2) + pow(ware[w, 2] - sto[s, 2], 2))
    return dist


print('Hello world')

warehouses = []
for i in range(ware_no):
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    u = rn.randint(20, 40) * 100
    f = rn.randint(10000, 30000)
    new_ware = ([0, xlab, ylab, u, f])
    warehouses.append(new_ware)
warehouses = np.array(warehouses)

stores = []
for i in range(sto_no):
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    d = rn.randint(20, 40) * 25
    new_sto = ([0, xlab, ylab, d])
    stores.append(new_sto)
stores = np.array(stores)

print("magazyny: \n", warehouses)
print("sklepy: \n", stores)


# sum of demand/supply

supp = sum_coll(warehouses, 3)
dem = sum_coll(stores, 3)
print("popyt:", dem)
print("podaż:", supp)

# cost
distance = dist_o_meter(warehouses, stores)
distance = np.transpose(distance)
print("\nodległosci: \n", distance)

mpl.figure(1)

mpl.plot(warehouses[:, 1], warehouses[:, 2], 'ro')
mpl.plot(stores[:, 1], stores[:, 2], 'bo')
mpl.axis([0, 100, 0, 100])
mpl.show()

# solver

problem = pu.LpProblem("FacLoc", pu.LpMinimize)

# zmienne dec

y = pu.LpVariable.dicts("y",
                        [(i, j) for i in range(ware_no)
                        for j in range(sto_no)], 0)
x = pu.LpVariable.dicts("x", range(ware_no), 0, 1, pu.LpBinary)

# funkcja

problem += (pu.lpSum(warehouses[i, 4] * x[i] for i in range(ware_no))
            + pu.lpSum(distance[i, j] * y[i, j] * stores[j, 3] for i in range(ware_no) for j in range(sto_no)))

# ograniczenia

for j in range(sto_no):
    problem += pu.lpSum(y[(i,j)] for i in range(ware_no)) == 1

for i in range(ware_no):
    problem += (pu.lpSum(y[(i,j)] * stores[(j, 3)] for j in range(sto_no))
    <= x[i] * warehouses[i, 3])


problem.solve()
print("status: ", pu.LpStatus[problem.status])


ya = np.zeros(np.shape(distance))
xa = np.zeros(ware_no)
for i in range(ware_no):
    xa[i] = x[i].varValue
    for j in range(sto_no):
        ya[i,j] = (y[i,j].varValue)
print(xa, "\n",ya)

great = []
bad = []
for lp in range(ware_no):
    if xa[lp] > 0:
        great.append([warehouses[lp, 1], warehouses[lp, 2]])
    else:
        bad.append([warehouses[lp, 1], warehouses[lp, 2]])

great = np.array(great)
bad = np.array(bad)

print(great, bad)

mpl.figure(2)

mpl.plot(great[:, 0], great[:, 1], 'go')
mpl.plot(bad[:, 0], bad[:, 1], 'rs')
mpl.plot(stores[:, 1], stores[:, 2], 'bo')
mpl.axis([0, 100, 0, 100])
mpl.show()

print("fajnie było")
