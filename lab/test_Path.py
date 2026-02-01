from collections.abc import MutableMapping
from pathlib import Path
from os.path import dirname, realpath, abspath, join

root = dirname(dirname(__file__))

class FF_Entry():
    def __init__(self, offset:int, p:Path, data:tuple=()):
        self.path = str(p)
        self.name = p.name
        self.relpath = self.path[offset:]
        self.mtime = p.stat().st_mtime
        self.data = data

fp = Path(__file__)
rp = Path(root)

class Maker():
    def __init__(self, root):
        self.__root = Path(root)
        print('root', self.__root)
        offset = len(str(self.__root / 'X')) - 1
        self.__gen = lambda p, *d : FF_Entry(offset, p, *d)

        self.rescan()
        print('data', len(self.__data))
        print(self.__data[0])

    def rescan(self):
        self.__data = tuple(x for x in self.__recurse(self.__root))

    def __iter__(self):
        for de in self.__data: yield de

    def __recurse(self, p:Path):
        ep = self.__gen(p)
        # print('entry:', ep.relpath, ep.mtime)
        # apply exclude criteria on ep
        cs = tuple(c for c in p.iterdir())
        # print('children:', len(cs))
        # print('fs', len(fs))
        # print('ds', len(ds))
        # check if dir entry valid (take criteria entry and data)
        ep.data = tuple(self.__gen(c) for c in cs if c.is_file())
        yield ep
        for dp in cs:
            if dp.is_dir():
                for x in self.__recurse(dp): yield x


m = Maker(root)
for de in m:
    print('de', de.relpath, len(de.data))

# fe = m.gen(fp)
# print(fe, fe.relpath, fe.name, fe.mtime)

# fp = m.gen(rp)
# print(fp, fp.relpath, fp.name, fp.mtime)

# fp = m.gen(__file__)
# print(type(fp).__name__)
# print('relpath', fp.relpath())
# print('name', fp.name)
# print('data', fp.data)
# if fp.data: print('data!')

# dp = m.gen(dirname(__file__))
# print(type(dp).__name__)
# print('relpath', dp.relpath())
# # print('dict', *dp.__dir__(), sep="\n")
# for x in dp.iterdir():
#     print(x)
