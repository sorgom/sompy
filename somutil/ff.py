"""some find file classes"""

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

    class __StartEntry:
        def __init__(self, root, name=''):
            self.name   = name
            self.path   = root
            self.is_dir = lambda : True
            self.stat   = lambda : stat(self.path)

    class __MapD():
        class __MapF():
            def __init__(self, entries:tuple, isCaseSense:bool, keyFunc):
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

        def __init__(self, entries:tuple, isCaseSense:bool, keyFunc):
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

        self.__reset()

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

    def mapping(self, keyFunc=lambda x : x):
        d = tuple(self.__iter__())
        m = self.__MapD(d, self.isCaseSense(), keyFunc)
        return d, m


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

    def __iter__(self):
        self.__reset()
        for x in self.__recDirs(self.__StartEntry(self.__root)): yield x

    def isCaseSense(self):
        if self.__caseSense is None: self.__caseSense = getCaseSense(self.__root)
        return self.__caseSense

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
