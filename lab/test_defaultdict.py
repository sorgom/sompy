from collections import defaultdict, Counter


def addSome(d:defaultdict):
    d['a'].append(1)
    d['b'].append(2)
    d['a'].append(3)


ddl = defaultdict(list)
addSome(ddl)
print(ddl)

cnt1 = Counter()
cnt1['a'] += 1
cnt1['b'] += 2
print(cnt1)
cnt2 = Counter()
cnt2['a'] += 1
cnt2['b'] += 2
print(cnt2 == cnt1)
cnt2['a'] += 1
print(cnt2 == cnt1)

lc = range(10)
print(lc)       

cnt1.clear()
cnt1.update(lc)
print(cnt1)

set1 = frozenset([1, 2, 3, 1])
set2 = {3, 4, 5}
print(set1 | set2)
print(set1 & set2)
print(set1 - set2)
print(set2 - set1)
print(set1 ^ set2)

d = dict()
di = d.items()
dv = d.values()
dk = d.keys()

d['a'] = 1
d['b'] = 2
print(di, dv, dk)

c = 'abc' * 5
print(c)
