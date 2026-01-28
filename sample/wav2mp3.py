"""
bulk wav to mp3 conversion
requires lame executable to be available within PATH

usage: this script [options] <source folder> <destination folder>
options
    -q  <quality> medium standard extreme insane or <kbps>
        default: hifi (recommended)
        kbps: 32 40 48 56 64 80 96 112 128 160 192 224 256 320
    -f  force overwrite existing mp3 files
        default: overwrites if wav is newer
    -c  clean mp3 files that have no source in wav folders with files
    -l  <int> limit of conversions per source / destination
    -t  <int> number of threads
    -h  this help
"""
from collections import Counter
from enum import Enum, auto
from os import remove, makedirs, system, name as oname
from os.path import join, isdir, isfile
from shutil import which, rmtree
import re

import sompy
from ff import FF_Re
from mtbase import MtBase
from progress import ProgressNum
from stopWatch import StopWatch
from toType import toInt, toBool



class Wav2Mp3(MtBase):
    "the wav2mp3 class"

    class ST(Enum):
        "enumeration for statistics"
        new = 0
        replaced = auto()
        removed = auto()
        errors = auto()

    def __init__(self, quality=None, force=None, limit=None, clean=None, numThreads=None, ignoreCase=True):
        super().__init__(numThreads)
        conv = 'lame'
        lame = which(conv)
        if lame is None:
            print('no', conv, 'wav2mp3 found on PATH.')
            exit(1)
        if quality:
            if quality in 'medium standard extreme insane 32 40 48 56 64 80 96 112 128 160 192 224 256 320':
                pass
            else:
                print('unsuitable quality:', quality)
                exit(1)
        else:
            quality = 'hifi'

        self.cmd = f'{lame} --quiet --preset {quality}'

        self.ignoreCase = ignoreCase  or oname != 'posix'

        def mkDirKey():
            if self.ignoreCase: return lambda e : e.relpath().upper()
            else: return lambda e : e.relpath()

        rx = re.compile(r'^(.*)\..*?$')
        def mkFileKey():
            if self.ignoreCase: return lambda e : rx.sub(r'\1', e.name()).upper()
            else: return lambda e : rx.sub(r'\1', e.name())

        def mkMp3Name():
            return lambda e : rx.sub(r'\1.mp3', e.name())

        self.dirKey     = mkDirKey()
        self.fileKey    = mkFileKey()
        self.mp3Name    = mkMp3Name()

        self.force  = toBool(force)
        self.limit  = toInt(limit) if limit else None
        self.clean  = toBool(clean)
        self.cnt    = ProgressNum('attempt no.', 15, 12)

        self.stats = Counter()

        self.info('threads', self.numThreads())
        self.info('limit', self.limit if self.limit else '--')
        print()

    @staticmethod
    def chkDir(dir):
        "check if folder exists"
        if not isdir(dir):
            print('no directory:', dir)
            return 1
        return 0

    def count(self, s:ST):
        self.stats[s.value] += 1

    def info(self, *args):
        self.cnt.info(*args)

    def mkMap(self, data:tuple):
        return { self.dirKey(de):{self.fileKey(fe):fe for fe in de.data} for de in data }

    def scanWav(self, rootWav):
        glWav = FF_Re(rootWav, r'^.*\.wav$', ignoreCase=self.ignoreCase)
        self.dataWav = tuple(d for d in glWav)
        if self.clean: self.mapWav = self.mkMap(self.dataWav)

    def scanMp3(self, rootMp3):
        glMp3 = FF_Re(rootMp3, r'^.*\.mp3$', ignoreCase=self.ignoreCase)
        self.dataMp3 = tuple(d for d in glMp3)
        self.mapMp3 = self.mkMap(self.dataMp3)

    @staticmethod
    def mDir(dir):
        if isfile(dir): remove(dir)
        makedirs(dir, exist_ok=True)

    def outLimit(self):
        return self.limit and self.cnt >= self.limit

    def w2m(self, wav:str, mp3:str, s:ST):
        if isdir(mp3): rmtree(mp3)
        # print(s.name, ':', mp3)
        res = system(f'{self.cmd} "{wav}" "{mp3}"')
        self.count(s if res == 0 else self.ST.errors)

    def process(self, *work):
        if self.outLimit(): return
        self.cnt.proceed()
        self.launch(self.w2m, *work)

    def transfer(self, rootWav:str, rootMp3:str):
        if self.chkDir(rootWav) + self.chkDir(rootMp3) > 0:
            exit(1)
        self.cnt.reset()
        self.stats.clear()
        sw = StopWatch()

        self.launch(self.scanWav, rootWav)
        self.launch(self.scanMp3, rootMp3)
        self.finish()

        sw.stop()
        self.info('scan', sw.str_ms())
        print()

        for deWav in self.dataWav:
            mMp3 = self.mapMp3.get(self.dirKey(deWav))
            if mMp3:
                for elWav in deWav.data:
                    elMp3 = mMp3.get(self.fileKey(elWav))
                    if elMp3:
                        if self.force or elWav.mtime() > elMp3.mtime():
                            self.process(elWav.path(), elMp3.path(), self.ST.replaced)
                    else:
                        pathMp3 = join(rootMp3, deWav.relpath(), self.mp3Name(elWav))
                        self.process(elWav.path(), pathMp3, self.ST.new)
            else:
                dirMp3 = join(rootMp3, deWav.relpath())
                self.mDir(dirMp3)
                for elWav in deWav.data:
                    pathMp3 = join(dirMp3, self.mp3Name(elWav))
                    self.process(elWav.path(), pathMp3, self.ST.new)

            if self.outLimit():
                break

        self.finish()
        if self.clean:
            for deMp3 in self.dataMp3:
                mWav = self.mapWav.get(self.dirKey(deMp3))
                if mWav:
                    for elMp3 in deMp3.data:
                        elWav = mWav.get(self.fileKey(elMp3))
                        if not elWav:
                            self.count(self.ST.removed)
                            remove(elMp3.path())

        sw.stop()
        self.info('attempts', self.cnt.count())
        for n, c in [(n.value, n.name) for n in self.ST]:
            self.info(c, self.stats[n])
        self.info('elapsed time', sw.str_sec())
        self.info('average', sw.avrg_str_sec(self.cnt.count()))

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    wav2mp3 = Wav2Mp3(quality=opts['q'], force=opts['f'], limit=opts['l'], numThreads=opts['t'], clean=opts['c'])

    while len(args) > 1:
        wav2mp3.transfer(*args[0:2])
        args = args[2:]
