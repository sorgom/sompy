"""some find file classes"""

from os import scandir
from os.path import join
import re

import sompy
from xglob import XGlob

class StartEntry:
    def __init__(self, path):
        self.name = ''
        self.path = path

class FF_Base:
    """find files base class"""
    def __init__(self, root:str):
        self.__root = root
        self._isF       = lambda e: e.is_file(follow_symlinks=False)
        self._isD       = lambda e: e.is_dir (follow_symlinks=False)

        self._checksTF  = [self._isF]
        self._checksXF  = []
        self._checksTD  = []
        self._checksXD  = []

        self._checkF    = lambda *p : all(f(*p) for f in self._checksTF) and not any(f(*p) for f in self._checksXF)
        self._checkTD   = lambda *p : all(f(*p) for f in self._checksTD)
        self._checkXD   = lambda *p : not any(f(*p) for f in self._checksXD)

        self._genF      = lambda e: e

        self.__errcnt = 0

    def addTF(self, func):
        self._checksTF.append(func)

    def addXF(self, func):
        self._checksXF.append(func)

    def addTD(self, func):
        self._checksTD.append(func)

    def addXD(self, func):
        self._checksXD.append(func)

    def errcnt(self):
        return self.__errcnt

    def __recDirs(self, de, relPath:str):
        #   stop recursion if directory name excluded
        if self._checkXD(de):
            try:
                relPath = join(relPath, de.name)
                with scandir(de.path) as iter:
                    es = list(iter)
                    fs = [e for e in [self._genF(e) for e in es if self._checkF(e)] if e]
                    ds = [e for e in es if self._isD(e)]
                    #   yield data if indicated
                    if self._checkTD(de, fs):
                        yield (relPath, fs, de)
                    for d in ds:
                        for x in self.__recDirs(d, relPath): yield x
            except Exception as e:
                self.__errcnt += 1
                pass

    def __iter__(self):
        self.__errcnt = 0
        for x in self.__recDirs(StartEntry(self.__root), ''): yield x

class FF_Re(FF_Base):
    """
    find files (and dirs) by regular expressions

    """

    def __init__(self, root:str, sTF:str=None, sXF:str=None, sTD:str=None, sXD:str=None, ignoreCase=False, unmatchedDirs=False):
        super().__init__(root)
        if ignoreCase:
            comp = lambda cp : re.compile(cp, re.I)
        else:
            comp = lambda cp : re.compile(cp)

        if sTF:
            self._rcTF = comp(sTF)
            if self._rcTF.groups:
                self._genF = self._genCatchF
            else:
                self.addTF(lambda e: self._rcTF.match(e.name))

        if sXF:
            self._rcXF = comp(sXF)
            self.addXF(lambda e: self._rcXF.match(e.name))

        if sTD:
            self._rcTD = comp(sTD)
            self.addTD(lambda e, fs: self._rcTD.match(e.name))

        if sXD:
            self._rcXD = comp(sXD)
            self.addXD(lambda e: self._rcXD.match(e.name))

        if not unmatchedDirs:
            self.addTD(lambda e, fs: fs)

    def _genCatchF(self, e):
        mo = self._rcTF.match(e.name)
        if mo:
            for x in mo.groups():
                if x: return (x, e)
            return (e.name, e)
        return None

class FF_XGlob(FF_Re):
    """
    find files (and dirs) using XGlob notation

    """
    def __init__(self, root:str, xgTF=None, xgXF=None, xgTD=None, xgXD=None, ignoreCase=False, unmatchedDirs=False):
        xg = XGlob()
        tr = lambda x : xg.glob2re(x)
        super().__init__(root, tr(xgTF), tr(xgXF), tr(xgTD), tr(xgXD), ignoreCase, unmatchedDirs)

if __name__ == '__main__':
    from os import name as oname
    from os.path import dirname, abspath
    from typing import Type

    import sompy
    from stopWatch import StopWatch

    testDir = abspath(join(dirname(__file__), '..'))

    def test(cls: Type[FF_Base], *params, dir:str=testDir, ignoreCase=False, unmatchedDirs=False):
        def pr(what, *cont):
            print(f'{what:<16}:', *cont)

        pr('class', cls.__name__)
        pr('params', *params)
        pr('dir', dir)
        nd = 0
        nf = 0
        sw = StopWatch()
        obj = cls(dir, *params, ignoreCase=ignoreCase, unmatchedDirs=unmatchedDirs)
        for d, fs, e in obj:
            nd += 1
            nf += len(fs)
        sw.stop()

        pr('folders', nd)
        pr('files', nf)
        pr('errors', obj.errcnt())
        pr('total time', sw.str_sec())
        pr('avrg time', sw.avrg_str_ms(nd), '/ folder')
        print()
        return nd

    test(FF_XGlob, ('(*).PY') , None, None, ('__pycache__', 'template', 'lab'), ignoreCase=True)
