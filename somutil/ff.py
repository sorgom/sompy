"""some find file classes"""

from os import scandir
from os.path import splitext, join
import re

class FF_Base:
    """find files base class"""
    def __init__(self, root:str):
        self.__root = root
        self.__data = []
        self.__errs = []
        self.__cnt = 0
        self.__recDirs()

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
                if fs:
                    self.__data.append((join(*dirs) if dirs else '', fs))
                    self.__cnt += len(fs)
                for d in ds:
                    self.__recDirs(*dirs, d)
        except:
            self.__errs.append(dd)

    def __iter__(self):
         for x in self.__data: yield x

    def data(self):
        return self.__data

    def count(self):
        return self.__cnt

    def errors(self):
        return self.__errs

    def errcnt(self):
        return len(self.__errs)

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
    def __init__(self, root:str, reFile:re.Pattern=None, reDir:re.Pattern=None):
        self._reF = reFile
        self._reD = reDir
        super().__init__(root)

    def myFile(self, entry):
        return entry if (not self._reF) or self._reF.match(entry.name) else None

    def myDir(self, entry):
        return (not self._reD) or self._reD.match(entry.name)

class FF_ReCatch(FF_Re):
    """find files with catching (and dirs) by regular expressions"""
    def __init__(self, root:str, reFile:re.Pattern, reDir:re.Pattern=None):
        super().__init__(root, reFile, reDir)

    def myFile(self, entry):
        mo = self._reF.match(entry.name)
        if mo:
            for x in mo.groups():
                if x: return (x, entry)
        return None

if __name__ == '__main__':
    from os.path import dirname, abspath
    testdir = abspath(join(dirname(__file__), '..', '..'))

    def test(obj:FF_Base):
        print('TYP:', type(obj))
        print('CNT:', obj.count())
        print('ERR:', obj.errcnt())
        print()

    # test(FF_Base(testdir))

    obj1 = FF_ExtNx(testdir, '.py')
    test(obj1)

    rx2 = re.compile(r'^(.*?)\.py$')
    obj2 = FF_ReCatch(testdir, rx2)
    test(obj2)

    print('same result?', obj1.count() == obj2.count())
    print()

    obj3 = FF_Ext(testdir, '.py', '.txt', '.sh')
    test(obj3)

    rx4 = re.compile(r'^(.*?)\.(?:py|txt|sh)$')
    obj4 = FF_ReCatch(testdir, rx4)
    test(obj4)

    print('same result?', obj3.count() == obj4.count())
    print()

    rx5 = re.compile(r'^(?:scr|DST).*$')
    obj5 = FF_ReCatch(testdir, rx4, rx5)
    test(obj5)
