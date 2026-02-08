from collections.abc import MutableMapping

class GhostDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__keyFunc = lambda k : k.upper()
        self._storage = dict(*(self.__keyFunc(arg) for arg in args), **{self.__keyFunc(k):v for k,v in kwargs.items()})

    def __getitem__(self, key):
        return self._storage[self.__keyFunc(key)]

    def __setitem__(self, key, value):
        self._storage[self.__keyFunc(key)] = value

    def __delitem__(self, key):
        del self._storage[self.__keyFunc(key)]

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def get(self, key, default=None):
        try:
            return self[self.__keyFunc(key)]
        except KeyError:
            return default

h = {'a':1, 'b':2}
print(*((k, v) for k,v in h.items()))
gd = GhostDict(**h)
print(gd['A'])

class FF_Map(MutableMapping):
    def __init__(self, keyFunc):
        self.__keyFunc = keyFunc
        self._storage = {}

    def __getitem__(self, e):
        return self._storage[self.__keyFunc(e)]

    def __setitem__(self, e, value):
        self._storage[self.__keyFunc(e)] = value

    def __delitem__(self, e):
        del self._storage[self.__keyFunc(e)]

    def __iter__(self):
        pass

    def __len__(self):
        return len(self._storage)

    def get(self, e, default=None):
        try:
            return self[e]
        except KeyError:
            return default

class FF_Map_F(FF_Map):
    def __init__(self, entries:tuple, keyFuncF=None):
        if keyFuncF is None:
            keyFunc = lambda e : e.name()
        else:
            keyFunc = lambda e : keyFuncF(e.name())
        super().__init__(keyFunc)
        self._storage = {keyFunc(e):e for e in entries}

class FF_Map_D(FF_Map):
    def __init__(self, entries:tuple, keyFuncF=None, keyFuncD=None):
        if keyFuncD is None:
            keyFunc = lambda e : e.relpath()
        else:
            keyFunc = lambda e : keyFuncD(e.relpath())
        super().__init__(keyFunc)
        self._storage = {keyFunc(e):FF_Map_F(e.data, keyFuncF) for e in entries}


class TE():
    def __init__(self, name, data:tuple=()):
        self.relpath = lambda : f'path/to/{name}'
        self.name = lambda : name
        self.data = data

    def __repr__(self):
        return f'<< {self.name()} >>'

tf = FF_Map_F((TE('wumpel.wav'), TE('lola.txt')))

eF = TE('wumpel.wav')
print(tf.get(eF))

fes = (TE('a.dat'), TE('b.dat'), TE('c.dat'))
de1 = TE('folder1', fes)
de2 = TE('folder2', fes)

td = FF_Map_D((de1, de2))
print(td.get(de2))
print(td.get(de2).get(fes[0]))

# tf = FF_Map((TE('wumpel.wav'), TE('lola.txt')), lambda e : e.name())
# print(tf.get(de))
# del tf[de]
# print(tf.get(de))




# print(de.relpath())
# print(de.name())
# print(de.data)
