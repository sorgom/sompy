
class A():
    def __init__(self):
        self.lf = lambda n: n

    def __iter__(self):
        for n in range(10):
            yield self.lf(n)

class B(A):
    def __init__(self):
        super().__init__()
        self.lf = lambda n: n * 5

print([n for n in A()])
print([n for n in B()])

result = """
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
[0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
"""

#   run lambda evaluation in array with "all" statement
def f1(n):
    print('f1')
    return n < 3

def f2(n):
    print('f2')
    return n == 2

def f3(n):
    print('f3')
    return n > 1

g1 = lambda n : f1(n)
g2 = lambda n : f2(n)
g3 = lambda n : f3(n)

pool = [g1, g2, g3]

ga = lambda n : all(g(n) for g in pool)

for n in [1, 2, 3]:
    print(n, ga(n))
