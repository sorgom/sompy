import sompy
from ff import *
from stopWatch import StopWatch

from os.path import basename, dirname, isdir
from os import makedirs, chdir
from shutil import rmtree
from typing import Type

myDir = dirname(__file__)
testDir = f'tmp_{basename(__file__)}_'
testDirs = (testDir, 'Lola', '$sys')
testFiles = ('wumpel.py', 'rumpel.PY', 'some.jpg')
testFuncs = (lambda c : c, lambda c : c.upper(), lambda c : c + '.$sys')

def touch(fn):
    with open(fn, 'w') as fh:
        fh.write('test only')

chdir(myDir)
if isdir(testDir): rmtree(testDir)

for dir, func in zip(testDirs, testFuncs):
    makedirs(dir)
    chdir(dir)
    for fn in testFiles: touch(func(fn))

chdir(myDir)

def test(cls: Type[FF_Base], *params, listEmpty=False, ignoreCase=False):
    def pr(what, *cont):
        print(f'{what:<20}:', *cont)

    pr('class', cls.__name__)
    pr('params', *(f'"{p}"' for p in params))
    pr('ignoreCase', ignoreCase)
    pr('listEmpty', listEmpty)
    dirs = []
    files = []
    sw = StopWatch()
    ff = cls(testDir, *params, listEmpty=listEmpty, ignoreCase=ignoreCase)
    for ffe in ff:
        dirs.append(f'"{ffe.relpath()}"')
        files.extend(fe.name() for fe in ffe.data)
    sw.stop()

    pr('folders visited', ff.dircnt())
    pr('folders listed', len(dirs))
    pr('files', len(files))
    pr('errors', ff.errcnt())
    pr('total time', sw.str_sec())
    pr('avrg time', sw.avrg_str_ms(ff.dircnt()), '/ visited folder')
    pr('folders', *dirs)
    pr('files', *files)
    print()
    return files

test(FF_XGlob, ('*.py') , 'RUMPEL.*', (r'\w+', ''), ('$*'), listEmpty=True)
test(FF_XGlob, ('*.(?:py|$sys)') , 'RUMPEL.*', ('[A-Z]*', '$*'), ignoreCase=True)

rmtree(testDir)
