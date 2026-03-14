"""
base bulk conversion class

usage: this script [options] <source folder> <destination folder>
options
    -f  force overwrite existing mp3 files
        default: overwrites if wav is newer
    -l  <int> limit of conversions per source / destination
    -t  <int> number of threads
    -h  this help

algorithm:
TODO: clean redundant target folders:
go through target
if equivalent source folder found:
clean target files without source equivalent

go through source folders, check target folders
if exists, check source files: new or overwrite
if not: create folder, all files new
"""
from collections import Counter
from enum import Enum, auto
from os import remove, makedirs, utime
from subprocess import run, DEVNULL
from os.path import join, isdir, isfile
from shutil import which, rmtree
import re

import sompy
from ff import FF_Re
from mtbase import MtBase
from progress import ProgressNum
from stopWatch import StopWatch
from toType import toInt, toBool

class ConvertBase(MtBase):
    "the converter class"

    class ST(Enum):
        "enumeration for statistics"
        new = 0
        replaced = auto()
        removed = auto()
        errors = auto()

    def __init__(self, conv, extSrc, extTrg, force=None, limit=None, clean=None, numThreads=None):
        super().__init__(numThreads)
        self.bin = which(conv)
        if self.bin is None:
            print('no', conv, 'found on PATH.')
            exit(1)

        self.cmd = self.bin

        self.extSrc = extSrc
        self.extTrg = extTrg

        rx = re.compile(r'^(.*)\..*?$')
        def mkTrgName():
            return lambda e : rx.sub(rf'\1.{extTrg}', e.name())

        self.keyFunc = lambda c : rx.sub(r'\1', c)
        self.trgName = mkTrgName()

        self.force  = toBool(force)
        self.limit  = max(0, toInt(limit)) if limit else None
        self.clean  = toBool(clean)
        self.cnt    = ProgressNum('transfer no.', 15, 12)

        self.stats = Counter()

        self.info('threads', self.numThreads())
        self.info('limit', self.limit if self.limit else '--')
        print()

    def count(self, s:ST):
        self.stats[s.value] += 1

    def info(self, *args):
        self.cnt.info(*args)

    @staticmethod
    def mDir(dir):
        if isfile(dir): remove(dir)
        makedirs(dir, exist_ok=True)

    def outLimit(self):
        return self.limit and self.cnt >= self.limit

    def s2t(self, feSrc, trg:str, s:ST):
        if isdir(trg): rmtree(trg)
        res = run(f'{self.cmd} "{feSrc.path()}" "{trg}"', stderr=DEVNULL, stdout=DEVNULL)
        if res.returncode == 0:
            self.count(s)
            t = feSrc.mtime()
            utime(trg, (t, t))
        else:
            self.count(self.ST.errors)

    def process(self, *work):
        if self.outLimit(): return
        self.cnt.proceed()
        self.launch(self.s2t, *work)

    def transfer(self, rootSrc:str, rootTrg:str):
        try:
            ffSrc = FF_Re(rootSrc, rf'^.*\.{self.extSrc}$', ignoreCase=True)
            ffTrg = FF_Re(rootTrg, rf'^.*\.{self.extTrg}$', ignoreCase=True)
        except Exception as e:
            print(e)
            return

        self.cnt.reset()
        self.stats.clear()
        sw = StopWatch()

        self.launch(lambda : ffSrc.update())
        self.launch(lambda : ffTrg.update())
        self.finish()


        sw.stop()
        self.info('scan', sw.str_ms())
        self.info(self.extSrc, ffSrc.dircnt())
        self.info(self.extTrg, ffTrg.dircnt())
        print()

        mapTrg = ffTrg.genMap(self.keyFunc)

        for deSrc in ffSrc:
            dirTrg = ffTrg.path(deSrc)
            mTrg   = mapTrg.get(deSrc)
            if mTrg:
                for feSrc in deSrc.data:
                    feTrg = mTrg.get(feSrc)
                    if feTrg:
                        if self.force or feSrc.mtime() > feTrg.mtime():
                            self.process(feSrc, feTrg.path(), self.ST.replaced)
                    else:
                        pathTrg = join(dirTrg, self.trgName(feSrc))
                        self.process(feSrc, pathTrg, self.ST.new)
            else:
                self.mDir(dirTrg)
                for feSrc in deSrc.data:
                    pathTrg = join(dirTrg, self.trgName(feSrc))
                    self.process(feSrc, pathTrg, self.ST.new)

            self.finish()

            if self.outLimit():
                break


        sw.stop()
        self.info('transfers', self.cnt.count())
        for n, c in [(n.value, n.name) for n in self.ST]:
            self.info(c, self.stats[n])
        self.info('elapsed time', sw.str_sec())
        self.info('average', sw.avrg_str_sec(self.cnt.count()))

# if __name__ == '__main__':
#     from docopts import docopts

#     opts, args = docopts(__doc__, reqArgs=True, all=True)

#     wav2mp3 = Wav2Mp3(quality=opts['q'], force=opts['f'], limit=opts['l'], numThreads=opts['t'])

#     while len(args) > 1:
#         wav2mp3.transfer(*args[0:2])
#         args = args[2:]
