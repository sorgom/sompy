"""some find file classes"""

from os import scandir, DirEntry
from os.path import join

class FF_Entry:
    def __init__(self, relPath:str, entry:DirEntry, files:tuple):
        self.rp = relPath
        self.de = entry
        self.fs = files

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

    def __reset(self):
        self.__errcnt = 0
        self.__dircnt = 0

    def __recDirs(self, de, relPath:str):
        self.__dircnt += 1
        #   stop recursion if directory name excluded
        if self._checkXD(de):
            try:
                relPath = join(relPath, de.name)
                with scandir(de.path) as iter:
                    es = tuple(iter)
                    fs = tuple(e for e in (self._genF(e) for e in es if self._checkF(e)) if e)
                    ds = tuple(e for e in es if self._isD(e))
                    #   yield data if indicated
                    if self._checkTD(de, fs):
                        yield FF_Entry(relPath, de, fs)
                    for d in ds:
                        for x in self.__recDirs(d, relPath): yield x
            except Exception:
                self.__errcnt += 1
                pass

    def __iter__(self):
        self.__reset()
        for x in self.__recDirs(StartEntry(self.__root), ''): yield x

import re
class FF_Re(FF_Base):
    """
    find files (and dirs) by regular expressions

    """
    #   local regex lambda generator
    class __MkCheck:
        def __init__(self, ignoreCase:bool=False):
            self.opts = [re.I] if ignoreCase else []
            self.groups = None

        def gen(self, pat:str):
            rx = re.compile(pat, *self.opts)
            self.groups = rx.groups
            return lambda e, *p : rx.match(e.name)

    def __init__(self, root:str, sTF:str=None, sXF:str=None, sTD:str=None, sXD:str=None, ignoreCase=False, unmatchedDirs=False):
        super().__init__(root)

        mkc = self.__MkCheck(ignoreCase)

        if sTF:
            check = mkc.gen(sTF)
            if mkc.groups:
                self._genChk = check
                self._genF   = self._genCatchF
            else:
                self.addCheckTF(check)

        if sXF:
            self.addCheckXF(mkc.gen(sXF))

        if sTD:
            self.addCheckTD(mkc.gen(sTD))

        if sXD:
            self.addCheckXD(mkc.gen(sXD))

        if not unmatchedDirs:
            self.addCheckTD(lambda e, fs: fs)

    def _genCatchF(self, e):
        mo = self._genChk(e)
        if mo:
            for x in mo.groups():
                if x: return (x, e)
            return (e.name, e)
        return None

from xglob import XGlob
class FF_XGlob(FF_Re):
    """
    find files (and dirs) using XGlob notation

    """
    def __init__(self, root:str, xgTF=None, xgXF=None, xgTD=None, xgXD=None, ignoreCase=False, unmatchedDirs=False):
        xg = XGlob()
        tr = lambda x : xg.glob2re(x)
        super().__init__(root, tr(xgTF), tr(xgXF), tr(xgTD), tr(xgXD), ignoreCase, unmatchedDirs)

if __name__ == '__main__':
    from os.path import dirname, abspath
    from typing import Type

    from stopWatch import StopWatch

    testDir = abspath(join(dirname(__file__), '..'))

    def test(cls: Type[FF_Base], *params, dir:str=testDir, ignoreCase=False, unmatchedDirs=False):
        def pr(what, *cont):
            print(f'{what:<16}:', *cont)

        pr('class', cls.__name__)
        pr('params', *params)
        pr('ignoreCase', ignoreCase)
        pr('unmatchedDirs', unmatchedDirs)
        pr('dir', dir)
        nd = 0
        nf = 0
        sw = StopWatch()
        ff = cls(dir, *params, ignoreCase=ignoreCase, unmatchedDirs=unmatchedDirs)
        tp = None
        for ffe in ff:
            nd += 1
            nf += len(ffe.fs)
            if tp is None and ffe.fs:
                tp = type(ffe.fs[0]).__name__
        sw.stop()

        pr('element type', tp)
        pr('folders visited', ff.dircnt())
        pr('folders listed', nd)
        pr('files', nf)
        pr('errors', ff.errcnt())
        pr('total time', sw.str_sec())
        pr('avrg time', sw.avrg_str_ms(ff.dircnt()), '/ visited folder')
        print()
        return nd

    test(FF_XGlob, ('(*).PY§?') , None, None, ('__pycache__', 'template', 'lab'), ignoreCase=True)
    test(FF_XGlob, ('*.pyc?') , 'som*', ('*util', 'samp*'), unmatchedDirs=True)
    test(FF_XGlob, ('*.pyc?') , 'som*', unmatchedDirs=True)
