cnr = 0

def chap():
    global cnr
    cnr += 1
    print('\n###### chapter', cnr)


chap()

import numpy as np


cvalues = [20.1, 20.8, 21.9, 22.5, 22.7, 21.8, 21.3, 20.9, 20.1]

C = np.array(cvalues)
print(C, type(C))
print(C * 9 / 5 + 32)

# import matplotlib.pyplot as plt

# plt.plot(C)
# plt.show()

chap()

a = np.arange(1, 7)
print(a)
# im Vergleich dazu nun range:
x = range(1, 7)
print(x)    # x ist ein Iterator
print(list(x))
# weitere arange-Beispiele:
x = np.arange(7.3)
print(x)
x = np.arange(0.5, 6.1, 0.8)
print(x)
x = np.arange(0.5, 6.1, 0.8, int)
print(x)

samples, spacing = np.linspace(1, 10, 5, 
                               endpoint=True, retstep=True)
print(samples, spacing)

A = np.array([ [3.4, 8.7, 9.9], 
               [1.1, -7.8, -0.7],
               [4.1, 12.3, 4.8],
               [1.1, -7.8, -0.7]
               ])
print(A)
print(A.ndim)
print(A.shape)
A.shape = (3, 4)
print(A)
print(A[1, 0])
