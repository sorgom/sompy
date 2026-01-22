"""some find file classes"""

from os import scandir
from os.path import splitext, join
import re

class FF_Base:
    """find files base class"""
    def __init__(self, root:str):
        self.__root = root

    def myFile(self, entry):
        return entry

    def myDir(self, _):
        return True

    def __recDirs(self, *dirs):
        try:
            dd = join(self.__root, *dirs)
            with scandir(dd) as iter:
                items = list(iter)
                fs = [e for e in [self.myFile(i) for i in items if i.is_file(follow_symlinks=False)] if e]
                ds = [i.name for i in items if i.is_dir(follow_symlinks=False) and self.myDir(i)]
                yield (join(*dirs) if dirs else '', fs)
                for d in ds:
                    for x in self.__recDirs(*dirs, d): yield x
        except:
            pass

    def __iter__(self):
         for x in self.__recDirs(): yield x

class FF_Ext(FF_Base):
    """find files by extensions"""
    def __init__(self, root:str, *ext:str):
        self.__ext = ext
        super().__init__(root)

    def myFile(self, entry):
        _, ext = splitext(entry.name)
        return entry if ext in self.__ext else None

class FF_ExtNx(FF_Base):
    """find files by extension, return names without"""
    def __init__(self, root:str, ext:str):
        self.__ext = ext
        super().__init__(root)

    def myFile(self, entry):
        base, ext = splitext(entry.name)
        return (base, entry) if ext == self.__ext else None

class FF_Re(FF_Base):
    """find files (and dirs) by regular expressions"""

    def __init__(self, root:str, sTF:str=None, sTD:str=None, sXF:str=None, sXD:str=None):
        super().__init__(root)
        self._rcTF = re.compile(sTF) if sTF else None
        self._rcTD = re.compile(sTD) if sTD else None
        self._rcXF = re.compile(rf'(?!{sXF})') if sXF else None
        self._rcXD = re.compile(rf'(?!{sXD})') if sXD else None
        self._mTF = lambda e: self._rcTF.match(e.name) if sTF else lambda e: True
        self._mTD = lambda e: self._rcTD.match(e.name) if sTD else lambda e: True
        self._mXF = lambda e: self._rcXF.match(e.name) if sXF else lambda e: True
        self._mXD = lambda e: self._rcXD.match(e.name) if sXD else lambda e: True

    @staticmethod
    def _reM(rx:re.Pattern, entry):
        return (not rx) or rx.match(entry.name)

    @staticmethod
    def _reX(rx:re.Pattern, entry):
        return (not rx) or not rx.match(entry.name)

    def myFile(self, entry):
        return entry if self._mTF(entry) and self._mXF(entry) else None

    def myDir(self, entry):
        return self._mTD(entry) and self._mXD(entry)

class FF_ReCatch(FF_Re):
    """find files with catching (and dirs) by regular expressions"""
    def __init__(self, root:str, sTF:str, sTD:str=None, sXF:str=None, sXD:str=None):
        super().__init__(root, sTF, sTD, sXF, sXD)

    def myFile(self, entry):
        if not self._mXF(entry): return None
        mo = self._rcTF.match(entry.name)
        if mo:
            for x in mo.groups():
                if x: return (x, entry)
        return None

if __name__ == '__main__':
    from os.path import dirname, abspath
    from stopwatch import StopWatch
    testdir = abspath(join(dirname(__file__), '..', '..'))

    sw = StopWatch()

    def test(obj:FF_Base):
        print('TYP:', type(obj))
        cnt = 0
        for d, fs in obj:
            cnt += len(fs)
        print('CNT:', cnt)
        sw.stop().ms().avrg_ms(cnt)
        print()
        return cnt
    # test(FF_Base(testdir))

    obj1 = FF_ExtNx(testdir, '.py')
    n1 = test(obj1)

    rx2 = r'^(.*?)\.py$'
    obj2 = FF_ReCatch(testdir, rx2)
    n2 = test(obj2)

    print('same result?', n1 == n2)
    print()

    obj3 = FF_Ext(testdir, '.py', '.txt', '.sh')
    n3 = test(obj3)

    rx4 = r'^(.*?)\.(?:py|txt|sh)$'
    obj4 = FF_ReCatch(testdir, rx4)
    n4 = test(obj4)

    print('same result?', n3 == n4)
    print()

    rx5 = re.compile(r'^(?:scr|DST).*$')
    obj5 = FF_ReCatch(testdir, rx4, rx5)
    test(obj5)

    obj3 = FF_Ext('C:', '.py', '.txt', '.sh')
    n3 = test(obj3)

    rx4 = r'^(.*?)\.(?:py|txt|sh)$'
    obj4 = FF_ReCatch('C:', rx4)
    n4 = test(obj4)

    print('same result?', n3 == n4)
    print()

    from typing import Type
    def test2(cls: Type[FF_Base], *params, dir:str=testdir):
        print('class:', cls)
        print('drive:', dir)
        obj = cls(dir, *params)
        nd = 0
        nf = 0
        for d, fs in obj:
            nd += 1
            nf += len(fs)
        sw.stop()

        print('files:', nf)
        print('dirs :', nd)
        print('time :', sw.str_sec())
        print('avrg :', sw.avrg_str_ms(nd), '/ dir')
        print()
        return nd

    test2(FF_ReCatch, rx4, dir='N:')
