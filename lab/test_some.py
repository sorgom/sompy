import re
d = { 'A':'wumpel', 'B':'lola'}
print('A' in d)
print('C' in d)
print('wumpel' in d)

rxd = re.compile(r'^(?:__pycache__|wumpel)$')
rxi = re.compile(r'^(?:System Volume Information|\$.*)$')
rxf = re.compile(r'^(?:__pycache__|wumpel)$')

dirs = ['__pycache__', 'data', 'xyz', 'wumpel', '$recycle.bin']

res = [x for x in dirs if not (rxd.match(x) or rxi.match(x))]
print(res)

# Counter value of unset key
from collections import Counter
cn = Counter()
cn['rf'] += 1
for c in ['rf', 'rd']:
    print(c, cn[c])

# list hash with list values
ll = [['A', [1, 2, 3, 4, 5]], ['B', [1, 2, 3, 4, 5]]]
dl = { c:l for c, l in ll }
for c, l in ll:
    if c == 'A': l.remove(2)
    if c == 'B': l.remove(3)
    dl.get(c).remove(4)

print(ll)
print(dl)

ll = ['A', 'B', 'C']
l2 = ll.copy()
for c in l2:
    ll.remove(c)
print(ll)

# remove nth element
def rmn(a:list, n:int):
    del(a[n:n+1])

a = [0, 1, 2, 3]

rmn(a, 1)
print(a)
rmn(a, 1)
print(a)
