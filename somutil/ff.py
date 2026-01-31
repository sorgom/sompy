"""some find file classes"""

from collections.abc import MutableMapping
from os import scandir, DirEntry, stat
from os.path import join, realpath, abspath

from dirTools import *

class FF_Entry:
    def __init__(self, offset:int, entry:DirEntry, data=None):
        self.relpath = self.__mkRel(offset)
        self.entry   = entry
        self.data    = data
        self.stat    = lambda : self.entry.stat()
        self.name    = lambda : self.entry.name
        self.path    = lambda : self.entry.path
        self.mtime   = lambda : self.entry.stat().st_mtime

    def __mkRel(self, offset):
        return lambda : self.entry.path[offset:]


class FF_Base:
    """find files base class"""

    def __init__(self, root:str, listEmpty=False):
        self.__root     = realpath(abspath(root))
        chkDir(self.__root)
        self._isF       = lambda e: e.is_file(follow_symlinks=False)
        self._isD       = lambda e: e.is_dir (follow_symlinks=False)

        self._checksTF  = [self._isF]
        self._checksXF  = []
        self._checksTD  = []
        self._checksXD  = []

        self._checkF    = lambda *p : all(f(*p) for f in self._checksTF) and not any(f(*p) for f in self._checksXF)
        self._checkTD   = lambda *p : all(f(*p) for f in self._checksTD)
        self._checkXD   = lambda *p : not any(f(*p) for f in self._checksXD)

        if not listEmpty: self.addCheckTD(lambda e, fs, *p: fs)

        offset = len(join(self.__root, ''))

        self._gen = self.__mkGen(offset)

        self.__caseSense = None

        self.reScan()

    def addCheckTF(self, func):
        self._checksTF.append(func)

    def addCheckXF(self, func):
        self._checksXF.append(func)

    def addCheckTD(self, func):
        self._checksTD.append(func)

    def addCheckXD(self, func):
        self._checksXD.append(func)

    def errcnt(self):
        return self.__errcnt

    def dircnt(self):
        return self.__dircnt

    def data(self):
        return self.__data

    def genMap(self, keyFuncF=None, keyFuncD=None):
        return self._FF_Map_D(self.__data, keyFuncF, keyFuncD)

    def __mkGen(self, offset:int):
        return lambda e, *p: FF_Entry(offset, e, *p)

    def __reset(self):
        self.__errcnt = 0
        self.__dircnt = 0

    def __recDirs(self, de):
        self.__dircnt += 1
        #   stop recursion if exclusion matched
        if self._checkXD(de):
            try:
                with scandir(de.path) as iter:
                    es = tuple(iter)
                    fs = tuple(e for e in (self._gen(e) for e in es if self._checkF(e)))
                    ds = tuple(e for e in es if self._isD(e))
                    #   yield data if indicated
                    if self._checkTD(de, fs):
                        yield self._gen(de, fs)
                    for d in ds:
                        for x in self.__recDirs(d): yield x
            except Exception:
                self.__errcnt += 1
                pass

    def reScan(self):
        self.__reset()
        self.__data = tuple(de for de in self.__recDirs(self.__StartEntry(self.__root)))

    def __iter__(self):
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
        return lambda e, *p : rx.match(e.name)

from xglob import XGlob
class FF_XGlob(FF_Re):
    """
    find files (and dirs) using XGlob notation

    """
    def __init__(self, root:str, xgTF=None, xgXF=None, xgTD=None, xgXD=None, listEmpty=False, ignoreCase=False):
        xg = XGlob()
        tr = lambda x : xg.glob2rp(x)
        super().__init__(root, tr(xgTF), tr(xgXF), tr(xgTD), tr(xgXD), listEmpty, ignoreCase)
