import matplotlib.pyplot as mpl
import numpy as np
import random as rn
import math as mt
import pulp

dim = [0, 100]
number = 5
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
    x = 0
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    u = rn.randint(20, 40) * 100
    f = rn.randint(10000, 30000)
    new_ware = ([x, xlab, ylab, u, f])
    warehouses.append(new_ware)
warehouses = np.array(warehouses)

stores = []
for i in range(sto_no):
    x = 0
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    d = rn.randint(20, 40) * 25
    new_sto = ([x, xlab, ylab, d])
    stores.append(new_sto)
stores = np.array(stores)

print("magazyny: \n", warehouses)
print("sklepy: \n", stores)

y = np.zeros((sto_no, ware_no))
# print(y)

# sum of demand/supply
supp = sum_coll(warehouses, 3)
dem = sum_coll(stores, 3)
print("popyt:", dem)
print("podaż:", supp)

# cost
distance = dist_o_meter(warehouses, stores)
print("\nodległosci: \n", distance)

mpl.plot(warehouses[:, 1], warehouses[:, 2], 'ro')
mpl.plot(stores[:, 1], stores[:, 2], 'bo')
mpl.axis([0, 100, 0, 100])
mpl.show()


print("fajnie było")
