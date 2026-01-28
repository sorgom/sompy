
from glob import glob
from os.path import isdir, join, dirname
from os import makedirs
from shutil import rmtree

class Wumpel():
    class NoDir(Exception):
        def __init__(self, dir:str):
            super().__init__(f'directory not found: {dir}')

    def trough(self):
        raise self.NoDir('some drive')


try:
    w = Wumpel()
    w.trough()
except Wumpel.NoDir as e:
    print(e)

def driveCase(dir:str):
    if isdir(dir):
        testDir = join(dir, '.__case_chk__')
        if isdir(testDir): rmtree(testDir)
        makedirs(testDir)
        for fn in '__H', '__h', '__H':
            with open(join(testDir, f'{fn}.xyz'), 'w') as fh:
                fh.write('...')
                fh.close()

        print('glob', len(glob(join(testDir, '*.xyz'))))

        rmtree(testDir)


driveCase(dirname(__file__))
driveCase('C:/UnixData')

import os
print(os.path.normcase("/Home/USER/Documents"))

from time import sleep

from pathlib import Path
from tempfile import TemporaryDirectory

def caseSensitiveDir(dir):
    with TemporaryDirectory(dir=dir) as td:
        tp = Path(td)
        (tp / 'x').touch()
        (tp / 'X').touch()
        return len(tuple(tp.iterdir())) > 1

print(caseSensitiveDir('C:'))
print(caseSensitiveDir('C:/UnixData'))
