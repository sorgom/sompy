cnr = 0

def chap():
    global cnr
    cnr += 1
    print('\n###### chapter', cnr)


chap()

import numpy as np
from random import gauss, normalvariate
import matplotlib.pyplot as plt
from collections import Counter

n = 1000
values = []
frequencies = Counter()

while len(values) < n:
    value = int(normalvariate(180, 30))
    if 130 < value < 230:
        frequencies[value] += 1
        values.append(value)
print(values[:7])

freq = list(frequencies.items())
freq.sort()


# plt.plot(*list(zip(*freq)))
# plt.show()



import random

def random_ones_and_zeros(p):
    while True:
        x = random.random()
        yield 1 if x < p else 0
        
def firstn(generator, n):
    for i in range(n):
        yield next(generator)

n = 1000000

firstn_values = firstn(random_ones_and_zeros(0.8), n)
print(sum(firstn_values) / n)

min_percent = 0.98  # corresponds to 0.98 %
max_percent = 1.06   # 6 %

chap()
sample = np.random.random_sample(12)
print(sample)
growthrates = (max_percent - min_percent) * sample + min_percent
print(growthrates)
