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
    -l  <int> limit of conversions per source
    -v  verbose
    -h  this help
"""

from datetime import datetime
from os import walk, remove, makedirs, system
from os.path import relpath, join, isdir, isfile, getmtime
from shutil import which, rmtree
import re

import sompy
from progress import ProgressWheel

class Wav2Mp3(object):
    "the converter class"
    def __init__(self, quality=None, force=None, verbose=False, limit=None):
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
        self.verbose = verbose
        self.force = force
        self.limit = int(limit) if limit else None
        self.cnt = 0
        self.errors = 0
        self.rxWav = re.compile(r'\.wave?$', re.I)

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

    def tPath(self, sPath:str):
        rp = relpath(sPath, self.sDir)
        if rp == '.': rp = ''
        rp = join(self.dDir, rp)
        self.mDir(rp)
        return rp

    def w2m(self, src:str, sDir:str, tDir:str):
        mp3 = self.rxWav.sub('.mp3', src)
        if mp3 == src: return False
        mp3 = join(tDir, mp3)
        wav = join(sDir, src)
        if isdir(mp3): rmtree(mp3)
        if self.force or (not isfile(mp3)) or (getmtime(wav) > getmtime(mp3)):
            res = system(f'{self.cmd} "{wav}" "{mp3}"')
            ok = res == 0
            if not ok: self.errors += 1
            return ok
        else:
            return False

    def transfer(self, sDir:str, dDir:str):
        if self.chkDir(sDir) + self.chkDir(dDir) > 0:
            exit(1)
        start = datetime.now()
        self.sDir = sDir
        self.dDir = dDir
        self.cnt = 0
        self.errors = 0

        pgw = ProgressWheel()

        cont = True

        for sDir, dirs, files in walk(sDir):
            if not cont: break
            tDir = self.tPath(sDir)
            for file in files:
                if self.w2m(file, sDir, tDir):
                    self.cnt += 1
                    if not self.verbose:
                        print(f'{self.cnt:>6}', end="\r")
                    if self.limit and self.cnt >= self.limit:
                        cont = False
                        break

        self.info('conversions', self.cnt)
        self.info('errors', self.errors)
        dt = datetime.now() - start
        self.info('elapsed time', dt)
        if self.cnt > 0:
            avg = dt / self.cnt
            self.info('average time', avg)

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    converter = Wav2Mp3(quality=opts['q'], force=opts['f'], verbose=opts['v'], limit=opts['l'])

    while len(args) > 1:
        converter.transfer(args.pop(0), args.pop(0))
