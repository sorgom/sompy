import re

rxp = re.compile(r'^(?:abc|def|efg)$')
rxn = re.compile(r'(?!^(?:abc|def|efg)$)')
rxx = re.compile(rf'(?!{rxp.pattern})')

cs = ['abc', 'def', 'efgh']

def test(rx):
    for c in cs:
        print('match:', rx.match(c))
    print()

test(rxp)
test(rxn)
test(rxx)

def wumpel(x):
    return 'C' if x == 'X' else None

c = r'^.*$'
print(type(c))
