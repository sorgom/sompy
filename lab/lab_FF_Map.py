import sompy
from ff import FF_Entry

class FF_Map():
    class __MapF():
        def __init__(self, entries:tuple, isCaseSense, keyFunc):
            if isCaseSense:
                self.__keyFunc = lambda e : keyFunc(e.name())
            else:
                self.__keyFunc = lambda e : keyFunc(e.name()).upper()

            self.__data = {self.__keyFunc(e):e for e in entries}

        def get(self, entry):
            return self.__data.get(self.__keyFunc(entry))

        def __len__(self):
            return len(self.__data)

        def keys(self):
            return self.__data.keys()



    def __init__(self, entries:tuple, isCaseSense=True):
        if isCaseSense:
            self.__keyFunc = lambda e : e.relpath()
        else:
            self.__keyFunc = lambda e : e.relpath().upper()
        self.__data = {self.__keyFunc(de):self.__MapF(de.data, isCaseSense, keyFunc) for de in entries}

    def get(self, entry):
        return self.__data.get(self.__keyFunc(entry))

    def __len__(self):
        return len(self.__data)

    def keys(self):
        return self.__data.keys()

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2: exit()
    import re
    from ff import *

    ff1 = FF_Base(argv[1])
    des1, m1 = ff1.mapping()

    for de in des1:
        print(de.name(), ':', *m1.get(de).keys())
        print()

    # rx = re.compile(r'^(.*)\..*?$')
    # keyFunc = lambda c : rx.sub(r'\1', c)
    # m = FF_Map(des, isCaseSense=ff.isCaseSense(), keyFunc=keyFunc)

    # for de in des:
    #     print(de.name(), ':', *m.get(de).keys())

    # if len(argv) < 3: exit()

    # print()

    # ff2 = FF_Base(argv[2])
    # des2 = tuple(e for e in ff2)
    # # m2 = FF_Map(des2, isCaseSense=ff.isCaseSense())

    # for de in des2:
    #     res = m1.get(de)
    #     print(de.name(), res)
