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
    -l  <int> limit of directory conversions per source / destination
    -t  <int> number of threads
    -v  verbose
    -h  this help
"""

from datetime import datetime
from os import remove, makedirs, system
from os.path import join, isdir, isfile, getmtime
from shutil import which, rmtree

import sompy
from progress import ProgressWheel
from toType import toInt, toBool
from ffnx import FFNX
from mtbase import MtBase

class Wav2Mp3(MtBase):
    "the converter class"
    def __init__(self, quality=None, force=None, verbose=None, limit=None, numThreads=None):
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
        self.cmd = f"{lame}{'' if verbose else ' --quiet'} --preset {quality}"
        self.verbose = toBool(verbose)
        self.force   = toBool(force)
        self.limit   = toInt(limit) if limit else None
        self.cnt = 0
        self.errors = 0

    @staticmethod
    def chkDir(dir):
        "check if folder exists"
        if not isdir(dir):
            print('no directory:', dir)
            return 1
        return 0

    @staticmethod
    def info(top:str, cont):
        print(f'{top:<20}:{str(cont):>20}')

    @staticmethod
    def mDir(dir):
        if isfile(dir): remove(dir)
        makedirs(dir, exist_ok=True)

    def outLimit(self):
        return self.limit and self.cnt >= self.limit

    def work(self, wav:str, mp3:str):
        if isdir(mp3): rmtree(mp3)
        res = system(f'{self.cmd} "{wav}" "{mp3}"')
        if res == 0:
            self.cnt += 1
            print('.', end='', flush=True)
        else:
            self.errors += 1
            print('X', end='', flush=True)

    def process(self, dir:str, mk:bool, wavs:set, mp3s:set={}):
        sDir = join(self.sRoot, dir)
        dDir = join(self.dRoot, dir)
        if mk: self.mDir(dDir)
        for name in sorted(wavs):
            sf = join(sDir, f'{name}.wav')
            df = join(dDir, f'{name}.mp3')
            if self.force or (not name in mp3s) or (getmtime(sf) > getmtime(df)):
                self.start(sf, df)
                if self.outLimit(): break

    def transfer(self, sRoot:str, dRoot:str):
        if self.chkDir(sRoot) + self.chkDir(dRoot) > 0:
            exit(1)
        begin = datetime.now()
        self.sRoot = sRoot
        self.dRoot = dRoot
        self.cnt = 0
        self.errors = 0

        self.info('threads', self.numThreads())

        pgw = ProgressWheel()

        lSrc = list(FFNX(sRoot, '.wav'))
        lDst = list(FFNX(dRoot, '.mp3'))
        hSrc = { dir:names for dir, names in lSrc }

        #   remove mp3 files if source has wav files and names not in list
        for dir, dns in lDst:
            sns = hSrc.get(dir)
            if sns:
                dels = dns - sns
                if dels:
                    print('delete:', dir, ':', *dels)
                    # for name in dels:
                    #     remove(join(dRoot, dir, f'{name}.mp3'))
                    dns -= dels

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

        self.info('conversions', self.cnt)
        self.info('errors', self.errors)
        dt = datetime.now() - begin
        self.info('elapsed time', dt)
        if self.cnt > 0:
            avg = dt / self.cnt
            self.info('average time', avg)

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    converter = Wav2Mp3(quality=opts['q'], force=opts['f'], verbose=opts['v'], limit=opts['l'], numThreads=opts['t'])

    while len(args) > 1:
        converter.transfer(args.pop(0), args.pop(0))
