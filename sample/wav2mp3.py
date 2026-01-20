"""
bulk wav to mp3 conversion
requires lame.exe to be available within PATH

usage: this script [options] <source folder> <destination folder>
options
    -q  <quality> medium standard extreme insane or <kbps>
        default: hifi (recommended)
        kbps: 32 40 48 56 64 80 96 112 128 160 192 224 256 320
    -f  force owerwrite existing mp3 files
        default: owerwrites if wav is newer
    -l  <int> limit of conversions per source / destination
        (due to multi threading only a rough number)
    -t  <int> number of threads
    -h  this help
"""

from datetime import datetime
from os import remove, makedirs, system
from os.path import join, isdir, isfile, getmtime
from shutil import which, rmtree

import sompy
from progress import ProgressNum
from toType import toInt, toBool
from ffnx import FFNX
from mtbase import MtBase

class Wav2Mp3(MtBase):
    "the converter class"
    def __init__(self, quality=None, force=None, limit=None, numThreads=None):
        super().__init__(numThreads)
        conv = 'lame.exe'
        lame = which(conv)
        if lame is None:
            print('no', conv, 'converter found on PATH.')
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
        self.force   = toBool(force)
        self.limit   = toInt(limit) if limit else None
        self.cnt = ProgressNum('converted', 20, 19)
        self.errors = 0
        self.info('threads', self.numThreads())
        if self.limit: self.info('limit', self.limit)
        print()

    @staticmethod
    def chkDir(dir):
        "check if folder exists"
        if not isdir(dir):
            print('no directory:', dir)
            return 1
        return 0

    def info(self, *args):
        self.cnt.info(*args)

    @staticmethod
    def mDir(dir):
        if isfile(dir): remove(dir)
        makedirs(dir, exist_ok=True)

    def outLimit(self):
        return self.limit and self.cnt >= self.limit

    def sFile(self, dir:str, name:str):
        return join(self.sRoot, dir, f'{name}.wav')

    def dFile(self, dir:str, name:str):
        return join(self.dRoot, dir, f'{name}.mp3')

    def w2m(self, wav:str, mp3:str):
        if isdir(mp3): rmtree(mp3)
        res = system(f'{self.cmd} "{wav}" "{mp3}"')
        if res == 0:
            self.cnt.proceed()
        else:
            self.errors += 1

    @staticmethod
    def newer(sf:str, df:str):
        return getmtime(sf) > getmtime(df)

    def process(self, dir:str, mk:bool, wavs:set, mp3s:set={}):
        if mk: self.mDir(join(self.dRoot, dir))
        for name in sorted(wavs):
            sf = self.sFile(dir, name)
            df = self.dFile(dir, name)
            if self.force or (not name in mp3s) or self.newer(sf, df):
                self.launch(self.w2m, sf, df)
                if self.outLimit(): break

    def transfer(self, sRoot:str, dRoot:str):
        if self.chkDir(sRoot) + self.chkDir(dRoot) > 0:
            exit(1)
        begin = datetime.now()
        self.sRoot = sRoot
        self.dRoot = dRoot
        self.cnt.reset()
        self.errors = 0


        lSrc = list(FFNX(sRoot, '.wav'))
        lDst = list(FFNX(dRoot, '.mp3'))
        hSrc = { dir:names for dir, names in lSrc }

        #   the cleaning
        #   if limit: no removal
        #   if forced: all mp3
        #   else: redundant and older
        if not self.limit:
            cnt = 0
            for dir, dns in lDst:
                sns = hSrc.get(dir)
                if sns:
                    dels = dns if self.force else dns - sns
                    chks = (dns - dels) & sns

                    for name in chks:
                        sf = self.sFile(dir, name)
                        df = self.dFile(dir, name)
                        if self.newer(sf, df):
                            dels.add(name)

                    if dels:
                        cnt += len(dels)
                        for name in dels:
                            remove(self.dFile(dir, name))
                        dns -= dels

            self.info('removed', cnt)

        hDst = { dir:names for dir, names in lDst }

        for dir, sns in lSrc:
            if self.outLimit(): break
            dns = hDst.get(dir)
            if dns is None:
                self.process(dir, True, sns)
            else:
                self.process(dir, False, sns, dns)

        self.finalize()

        print()

        self.info('errors', self.errors)
        dt = datetime.now() - begin
        self.info('elapsed time', dt)
        if self.cnt > 0:
            avg = dt / self.cnt.count()
            self.info('average time', avg)
        print()

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    converter = Wav2Mp3(quality=opts['q'], force=opts['f'], limit=opts['l'], numThreads=opts['t'])

    while len(args) > 1:
        converter.transfer(*args[0:2])
        args = args[2:]
