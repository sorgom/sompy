"""some find file classes"""

from collections.abc import MutableMapping
from pathlib import Path

import sompy
from dirTools import *

class FF_Entry():
    def __init__(self, offset:int, p:Path, data:tuple=()):
        self.path = str(p)
        self.name = p.name
        self.relpath = self.path[offset:]
        self.mtime = p.stat().st_mtime
        self.data = data

class FF_Base:
    """find files base class"""

    def __init__(self, root:str, listEmpty=False):
        chkDir(root)
        self.__root = Path(root)
        offset = len(str(self.__root / 'X')) - 1
        self.__gen = lambda p, *d : FF_Entry(offset, p, *d)
        print('root', str(self.__root))

        self._checksTF  = []
        self._checksXF  = []
        self._checksTD  = []
        self._checksXD  = []

        self._checkF    = lambda fe : all(c(fe) for c in self._checksTF) and not any(c(fe) for c in self._checksXF)
        self._checkTD   = lambda de : all(c(de) for c in self._checksTD)
        self._checkXD   = lambda de : not any(c(de) for c in self._checksXD)

        if not listEmpty: self.addCheckTD(lambda de: de.data)

        self.__caseSense = None

        self.__data = None

    def addCheckTF(self, func):
        self._checksTF.append(func)

    def addCheckXF(self, func):
        self._checksXF.append(func)

    def addCheckTD(self, func):
        self._checksTD.append(func)

    def addCheckXD(self, func):
        self._checksXD.append(func)

    def errcnt(self):
        self.__chkData()
        return self.__errcnt

    def dircnt(self):
        self.__chkData()
        return self.__dircnt

    def size(self):
        self.__chkData()
        return len(self.__data)

    def genMap(self, keyFuncF=None, keyFuncD=None):
        self.__chkData()
        return self._FF_Map_D(self.__data, keyFuncF, keyFuncD)

    def __chkData(self):
        if self.__data is None: self.update()

    def __reset(self):
        self.__errcnt = 0
        self.__dircnt = 0

    def update(self):
        self.__reset()
        self.__data = tuple(x for x in self.__recurse(self.__root))

    def __iter__(self):
        self.__chkData()
        for de in self.__data: yield de

    def __recurse(self, p:Path):
        self.__dircnt += 1
        de = self.__gen(p)
        #   stop recursion if exclusion matched
        if self._checkXD(de):
            try:
                cs = tuple(c for c in p.iterdir())
                de.data = tuple(fe for fe in (self.__gen(c) for c in cs if c.is_file()) if self._checkF(fe))
                # print(de.name, len(de.data))
                if self._checkTD(de):
                    # print('take')
                    yield de
                for c in cs:
                    if c.is_dir():
                        for x in self.__recurse(c): yield x
            except Exception as e:
#                print(e)
                self.__errcnt += 1

    class _FF_Map(MutableMapping):
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

    class _FF_Map_F(_FF_Map):
        def __init__(self, entries:tuple, keyFuncF=None):
            if keyFuncF is None:
                keyFunc = lambda e : e.name
            else:
                keyFunc = lambda e : keyFuncF(e.name)
            super().__init__(keyFunc)
            self._storage = {keyFunc(e):e for e in entries}

    class _FF_Map_D(_FF_Map):
        def __init__(self, entries:tuple, keyFuncF=None, keyFuncD=None):
            if keyFuncD is None:
                keyFunc = lambda e : e.relpath
            else:
                keyFunc = lambda e : keyFuncD(e.relpath)
            super().__init__(keyFunc)
            self._storage = {keyFunc(e):FF_Base._FF_Map_F(e.data, keyFuncF) for e in entries}

import re
class FF_Re(FF_Base):
    """
    find files (and dirs) by regular expressions

    """
    def __init__(self, root:str, sTF:str=None, sXF:str=None, sTD:str=None, sXD:str=None, listEmpty=False, ignoreCase=False):
        super().__init__(root, listEmpty)

        if sTF:
            self.addCheckTF(self.__genRX(sTF, ignoreCase))

        if sXF:
            self.addCheckXF(self.__genRX(sXF, ignoreCase))

        if sTD:
            self.addCheckTD(self.__genRX(sTD, ignoreCase))

        if sXD:
            self.addCheckXD(self.__genRX(sXD, ignoreCase))

    @staticmethod
    def __genRX(pat:str, ignoreCase:bool):
        opts = [re.I] if ignoreCase else []
        rx = re.compile(pat, *opts)
        return lambda e : rx.match(e.name)

from xglob import XGlob
class FF_XGlob(FF_Re):
    """
    find files (and dirs) using XGlob notation

    """
    def __init__(self, root:str, xgTF=None, xgXF=None, xgTD=None, xgXD=None, listEmpty=False, ignoreCase=False):
        xg = XGlob()
        tr = lambda x : xg.glob2rp(x)
        super().__init__(root, tr(xgTF), tr(xgXF), tr(xgTD), tr(xgXD), listEmpty, ignoreCase)

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2: exit()
    from stopWatch import StopWatch
    sw = StopWatch()
    ffx = FF_XGlob(argv[1], '*.py')
    ffx.update()
    sw.stop().sec()
    print('ffx', ffx.size())
