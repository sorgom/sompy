import sompy
from ff import *
from stopWatch import StopWatch

from os import makedirs, chdir
from os.path import basename, dirname, isdir, abspath
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory
from time import sleep
from typing import Type

myDir = dirname(__file__)
testDirs = ('wumpel', 'Lola', '$sys')
testFiles = ('wumpel.py', 'rumpel.PY', 'some.jpg')
testFuncs = (lambda c : c, lambda c : c.upper(), lambda c : c + '.$sys')

tmp = TemporaryDirectory(dir=myDir)
testDir = tmp.name
tp = Path(tmp.name)
for subd, func in zip(testDirs, testFuncs):
    tp = tp / subd
    tp.mkdir()
    for fn in testFiles:
        (tp / func(fn)).touch()


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

    # md = ff.genMap()
    # for de in ff:
    #     mf = md.get(de)
    #     print
    #     for fe in de.data:
    #         print(mf.get(fe))

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
