from pathlib import Path
from os.path import dirname, realpath, abspath, join

p = Path(dirname(dirname(__file__)))
print(p)
print(p.name)
print(len(str(p / '1')))
print(str(p / '1')[20:])

class FF_Path(Path):
    def __init__(self, offset:int, p, data:tuple=()):
        super().__init__(p)
        print('self', str(self))
        self.relpath = lambda : str(self)[offset:]
        self.data = data
    def iterdir(self):
        Path(self).iterdir()


fp = FF_Path(12, dirname(__file__))

print(fp.__fspath__())
print(fp.relpath())

fp2 = Path(fp)

class Maker():
    def __init__(self, root):
        self.__root = Path(root)
        print('root', self.__root)
        offset = len(str(self.__root / 'a')) - 1
        print('offset', offset)
        def _mkgen(offset):
            return lambda *args : FF_Path(offset, *args)
        self.gen = _mkgen(offset)
        # self.gen = lambda *args : FF_Path(offset, *args)


m = Maker(p)
fp = m.gen(__file__)
print(type(fp).__name__)
print('relpath', fp.relpath())
print('name', fp.name)
print('data', fp.data)
if fp.data: print('data!')

dp = m.gen(dirname(__file__))
print(type(dp).__name__)
print('relpath', dp.relpath())
# print('dict', *dp.__dir__(), sep="\n")
for x in dp.iterdir():
    print(x)
