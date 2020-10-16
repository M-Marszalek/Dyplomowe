import matplotlib.pyplot as mpl
import numpy as np
import random as rn

dim = [0,100]
number = 5

print('Hello world')
p = 1
facilities = []
while p <= number:
    x = 0
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    u = rn.randint(10, 50) * 100
    fac = ([x, xlab, ylab, u])
    facilities.append(fac)
    p += 1
facilities = np.array(facilities)

p = 1
customer = []
while p < number * 3:
    x = 0
    xlab = rn.randint(dim[0], dim[1])
    ylab = rn.randint(dim[0], dim[1])
    u = rn.randint(10, 50) * 20
    cus = ([x, xlab, ylab, u])
    customer.append(cus)
    p += 1
customer = np.array(customer)
print(facilities)
print(customer)

prod = 0
for i in range(len(facilities[:, 0])):
    prod += facilities[i, 3]

zap = 0
for i in range(len(customer[:, 0])):
    zap += customer[i, 3]

print(zap)
print(prod)


mpl.plot(facilities[:,1], facilities[:,2], 'ro')
mpl.plot(customer[:,1], customer[:,2], 'bo')
mpl.axis([0, 100, 0, 100])
mpl.show()

print("fajnie było")
