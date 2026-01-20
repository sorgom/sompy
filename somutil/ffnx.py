from os import walk
from os import scandir
from os.path import relpath, splitext, join
import re

class FFNX:
    """find file names by extension recursion"""
    def __init__(self, root:str, ext:str):
        self.__ext = ext
        self.__root = root

    def __iter__(self):
        for dir, _, files in walk(self.__root):
            dir = relpath(dir, self.__root)
            if dir == '.': dir = ''
            names = (n for n, x in [splitext(f) for f in files] if x == self.__ext)
            if names: yield(dir, set(names))

class FFXGL:
    """exclude files and dirs by glob recursion"""
    def __init__(self, root:str, glD:str, glF:str):
        self.__rxD = self.__gl2rx(glD)
        self.__rxF = self.__gl2rx(glF)
        self.__root = root
        self.__data = []
        self.__err = 0
        self.__cnt = 0
        self.__recDirs()

    @staticmethod
    def __gl2rx(gl:str):
        gl = re.sub(r'[\\^],', ',', re.sub(r'([^\\^]),\s*', r'\1|', re.sub(r'([$^])', r'\\\1', gl.strip()))).replace('.', '\\.').replace('*', '.*').replace('?', '.')
        return re.compile(rf'^(?:{gl})$')

    def __recDirs(self, *dirs):
        try:
            dd = join(self.__root, *dirs)
            with scandir(dd) as items:
                fs = set()
                ds = []
                for i in items:
                    if i.is_file() :
                        if not self.__rxF.match(i.name):
                            fs.add(i.name)
                    elif i.is_dir():
                        if not self.__rxD.match(i.name):
                            ds.append(i.name)
                self.__data.append((join(*dirs) if dirs else '', fs))
                self.__cnt += len(fs)
                for d in ds:
                    self.__recDirs(*dirs, d)
        except:
            print('E:', dd)
            self.__err += 1

    def __iter__(self):
         for x in self.__data: yield x

    def data(self):
        return self.__data

    def count(self):
        return self.__cnt

    def errors(self):
        return self.__err


if __name__ == '__main__':
    from os.path import dirname, abspath
    sd = abspath(dirname(__file__) + '/../..')
    print('test FFXGL:', sd)
    fg = FFXGL(sd, 'im*, .git, __pycache__, tmp, tmp_*, [Ff]*, $*,System Volume Information', '*.pyc, *.mp3')
    for x in fg:
        print(',', end='')
    print()
    print('dirs  :', len(fg.data()))
    print('files :', fg.count())
    print('errors:', fg.errors())
