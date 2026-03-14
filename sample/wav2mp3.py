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
TODO: clean redundant mp3 folders:
go through mp3
if equivalent wav folder found:
clean mp3 files without wav equivalent

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

    def w2m(self, feWav, mp3:str, s:ST):
        if isdir(mp3): rmtree(mp3)
        res = run(f'{self.cmd} "{feWav.path()}" "{mp3}"', stderr=DEVNULL, stdout=DEVNULL)
        if res.returncode == 0:
            self.count(s)
            t = feWav.mtime()
            utime(mp3, (t, t))
        else:
            self.count(self.ST.errors)

    def process(self, *work):
        if self.outLimit(): return
        self.cnt.proceed()
        self.launch(self.w2m, *work)

    def transfer(self, rootWav:str, rootMp3:str):
        try:
            ffWav = FF_Re(rootWav, r'^.*\.wav$', ignoreCase=True)
            ffMp3 = FF_Re(rootMp3, r'^.*\.mp3$', ignoreCase=True)
        except Exception as e:
            print(e)
            return

        self.cnt.reset()
        self.stats.clear()
        sw = StopWatch()

        self.launch(lambda : ffWav.update())
        self.launch(lambda : ffMp3.update())
        self.finish()


        sw.stop()
        self.info('scan', sw.str_ms())
        self.info('wav', ffWav.dircnt())
        self.info('mp3', ffMp3.dircnt())
        print()

        mapMp3 = ffMp3.genMap(self.keyFunc)

        for deWav in ffWav:
            dirMp3 = ffMp3.path(deWav)
            mMp3   = mapMp3.get(deWav)
            if mMp3:
                for feWav in deWav.data:
                    feMp3 = mMp3.get(feWav)
                    if feMp3:
                        if self.force or feWav.mtime() > feMp3.mtime():
                            self.process(feWav, feMp3.path(), self.ST.replaced)
                    else:
                        pathMp3 = join(dirMp3, self.mp3Name(feWav))
                        self.process(feWav, pathMp3, self.ST.new)
            else:
                self.mDir(dirMp3)
                for feWav in deWav.data:
                    pathMp3 = join(dirMp3, self.mp3Name(feWav))
                    self.process(feWav, pathMp3, self.ST.new)

            self.finish()

            if self.outLimit():
                break


        sw.stop()
        self.info('transfers', self.cnt.count())
        for n, c in [(n.value, n.name) for n in self.ST]:
            self.info(c, self.stats[n])
        self.info('elapsed time', sw.str_sec())
        self.info('average', sw.avrg_str_sec(self.cnt.count()))

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    wav2mp3 = Wav2Mp3(quality=opts['q'], force=opts['f'], limit=opts['l'], numThreads=opts['t'])

    while len(args) > 1:
        wav2mp3.transfer(*args[0:2])
        args = args[2:]
