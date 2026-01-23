
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

gp = lambda *p : print(*p)
gp('hello', 'world')

def buildLambda(w1:int, w2:int):
    return lambda top, cont: print(f'{top:<{w1}}:{str(cont):>{w2}}')

ll = buildLambda(20, 19)
ll('hello', 'world')

class TL:
    def __init__(self, cap:str='count', w1:int=10, w2:int=9):
        def buildLInfo():
            return lambda top, cont: print(f'{top:<{w1}}:{str(cont):>{w2}}')
        def buildPgr():
            return lambda : print(f'{cap:<{w1}}:{str(self.__cnt):>{w2}}', end="\r")

        self.info = buildLInfo()

        self.__prinf = buildPgr()
        self.__cnt = 0

    def proceed(self):
        self.__cnt += 1
        self.__prinf()

tl = TL()
tl.info('hello', 'world')
tl.proceed()
tl.proceed()
print()

import re
ignorC = False
def buildRe(pat:str):
    opts = [re.I] if ignorC else []
    rx = re.compile(pat, *opts)
    return lambda c, *p : rx.match(c)

def test(func):
    for c in ('some.py', 'some.txt', 'some.PY'):
        print(c, func(c))

test(buildRe('^(.*)\.py$'))

ignorC = True
test(buildRe('^.*\.(py)$'))
