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
    -l  <int> limit of conversions per source / destination
    -t  <int> number of threads
    -h  this help


algorithm:
go through source dirs, check target dirs
if target dir not found in map:
    remove target dir if exists
else:
    go through source files
    if target file not found:
        remove target file if exists

this ensures that target files and dirs have same case as source ones

no cleaning of target folders

"""
from collections import Counter
from enum import Enum, auto
from os import remove, makedirs, system
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

    def __init__(self, quality=None, force=None, limit=None, clean=None, numThreads=None):
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


        rx = re.compile(r'^(.*)\..*?$')
        def mkMp3Name():
            return lambda e : rx.sub(r'\1.mp3', e.name())

        self.keyFunc = lambda c : rx.sub(r'\1', c)

        self.mp3Name    = mkMp3Name()

        self.force  = toBool(force)
        self.limit  = max(0, toInt(limit)) if limit else None
        self.clean  = toBool(clean)
        self.cnt    = ProgressNum('attempt no.', 15, 12)

        self.stats = Counter()

        self.info('threads', self.numThreads())
        self.info('limit', self.limit if self.limit else '--')
        print()

    def count(self, s:ST):
        self.stats[s.value] += 1

    def info(self, *args):
        self.cnt.info(*args)

    def scanWav(self, rootWav):
        self.dataWav, self.mapWav = FF_Re(rootWav, r'^.*\.wav$', ignoreCase=True).mapping(self.keyFunc)

    def scanMp3(self, rootMp3, listEmpty=False):
        self.dataMp3, self.mapMp3 = FF_Re(rootMp3, r'^.*\.mp3$', listEmpty=listEmpty, ignoreCase=True).mapping(self.keyFunc)

    @staticmethod
    def mDir(dir):
        if isfile(dir): remove(dir)
        makedirs(dir, exist_ok=True)

    @staticmethod
    def rmDir(dir):
        print('remove:', dir)
        if isfile(dir): remove(dir)
        if isdir(dir): rmtree(dir)

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
        self.cnt.reset()
        self.stats.clear()
        sw = StopWatch()

        self.launch(self.scanWav, rootWav)
        self.launch(self.scanMp3, rootMp3, True)
        self.finish()

        sw.stop()
        self.info('scan', sw.str_ms())
        print()

        if self.force and not self.limit:
            for deMp3 in self.dataMp3:
                if self.mapWav.get(deMp3):
                    self.rmDir(deMp3.path())
            self.scanMp3(rootMp3)

        for deWav in self.dataWav:
            mMp3 = self.mapMp3.get(deWav)
            if mMp3:
                for elWav in deWav.data:
                    elMp3 = mMp3.get(elWav)
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
        # if self.clean:
        #     for deMp3 in self.dataMp3:
        #         mWav = self.mapWav.get(deMp3)
        #         if mWav:
        #             for elMp3 in deMp3.data:
        #                 elWav = mWav.get(elMp3)
        #                 if not elWav:
        #                     self.count(self.ST.removed)
        #                     remove(elMp3.path())
        #                     # print(f'remove({elMp3.path()})')

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
