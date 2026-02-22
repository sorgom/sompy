"""some find file classes"""

from collections.abc import MutableMapping
from os import scandir, DirEntry, stat
from os.path import join, realpath, abspath

from dirTools import *

class FF_Entry:
    """wrapper for os.DirEntry"""
    def __init__(self, offset:int, entry:DirEntry, data=tuple()):
        self.relpath = lambda : self.entry.path[offset:]
        self.stat    = lambda : self.entry.stat()
        self.name    = lambda : self.entry.name
        self.path    = lambda : self.entry.path
        self.mtime   = lambda : self.entry.stat().st_mtime
        self.entry   = entry
        self.data    = data


class FF_Base:
    """find files base class"""

    def __init__(self, root:str, listEmpty=False):
        self.__root     = realpath(abspath(root))
        chkDir(self.__root)

        self._checksTF  = []
        self._checksXF  = []
        self._checksTD  = []
        self._checksXD  = []

        self._checkF    = lambda fe : all(c(fe) for c in self._checksTF) and not any(c(fe) for c in self._checksXF)
        self._checkTD   = lambda de : all(c(de) for c in self._checksTD)
        self._checkXD   = lambda de : not any(c(de) for c in self._checksXD)

        if not listEmpty: self.addCheckTD(lambda de: de.data)

        offset = len(join(self.__root, ''))

        self._gen = self.__mkGen(offset)

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

    def root(self):
        return self.__root

    def errcnt(self):
        self.__chkData()
        return self.__errcnt

    def dircnt(self):
        self.__chkData()
        return self.__dircnt

    def path(self, e:FF_Entry):
        return join(self.__root, e.relpath())

    def genMap(self, keyFuncF=None, keyFuncD=None):
        self.__chkData()
        return self._FF_Map_D(self.__data, keyFuncF, keyFuncD)

    def __mkGen(self, offset:int):
        return lambda e, *p: FF_Entry(offset, e, *p)

    def __reset(self):
        self.__errcnt = 0
        self.__dircnt = 0

    def __recDirs(self, d:DirEntry):
        self.__dircnt += 1
        #   stop recursion if exclusion matched
        de = self._gen(d)
        if self._checkXD(de):
            try:
                # print('scan', d.path)
                with scandir(d.path) as iter:
                    # print('OK ...')
                    es = tuple(iter)
                    # fs = tuple(e for e in es if e.is_file())
                    de.data = tuple(fe for fe in (self._gen(f) for f in (e for e in es if e.is_file())) if self._checkF(fe))
                    # print('data', len(de.data))
                    # ds = tuple(e for e in es if self._isD(e))
                    #   yield data if indicated
                    if self._checkTD(de):
                        # print('yield')
                        yield de
                    for e in es:
                        # print(e.name, e.is_dir())
                        if e.is_dir():
                            for x in self.__recDirs(e): yield x
            except Exception as e:
                # print(e)
                self.__errcnt += 1
                pass

    def update(self):
        self.__reset()
        self.__data = tuple(de for de in self.__recDirs(self.__StartEntry(self.__root)))

    def __chkData(self):
        if self.__data is None: self.update()

    def __iter__(self):
        self.__chkData()
        for de in self.__data: yield de

    def isCaseSense(self):
        if self.__caseSense is None: self.__caseSense = getCaseSense(self.__root)
        return self.__caseSense

    class __StartEntry:
        def __init__(self, root, name=''):
            self.name   = name
            self.path   = root
            self.is_dir = lambda : True
            self.stat   = lambda : stat(self.path)

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
            for k in self._storage.keys(): yield k

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
                keyFunc = lambda e : e.name()
            else:
                keyFunc = lambda e : keyFuncF(e.name())
            super().__init__(keyFunc)
            self._storage = {keyFunc(e):e for e in entries}

    class _FF_Map_D(_FF_Map):
        def __init__(self, entries:tuple, keyFuncF=None, keyFuncD=None):
            if keyFuncD is None:
                keyFunc = lambda e : e.relpath()
            else:
                keyFunc = lambda e : keyFuncD(e.relpath())
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
        return lambda e : rx.match(e.name())

from xglob import XGlob
from itertools import batched

class FF_XGlob(FF_Re):
    """
    find files (and dirs) using XGlob notation

    """
    def __init__(self, root:str, xgTF=None, xgXF=None, xgTD=None, xgXD=None, listEmpty=False, ignoreCase=False, xglobFile=None):
        if xglobFile:
            xgTF, xgXF, xgTD, xgXD = self.f2xglob(xglobFile)

        xg = XGlob()
        tr = lambda x : xg.glob2rp(x)
        super().__init__(root, tr(xgTF), tr(xgXF), tr(xgTD), tr(xgXD), listEmpty, ignoreCase)

    @staticmethod
    def f2xglob(fp:str):
        map = XGlob.f2h(fp)
        return tuple(map.get(c) for c in ('TF', 'XF', 'TD', 'XD'))

if __name__ == '__main__':
    from sys import argv
    if len(argv) < 2: exit()
    from stopWatch import StopWatch

    sw = StopWatch()
    args = (arg if arg else None for arg in argv[1:])
    ffx = FF_XGlob(*args)
    ffx.update()
    sw.stop().sec()
    print(ffx.dircnt())
    # for e in ffx:
    #     print(e.name())

    rx = re.compile(r'^(.*)\..+$')
    m = ffx.genMap(lambda c : rx.sub(r'\1', c))
    for de in ffx:
        mf = m.get(de)
        for fe in de.data:
            r = mf.get(fe)
            print(r.name())
