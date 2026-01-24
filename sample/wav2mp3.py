"""
bulk wav to mp3 conversion
requires lame.exe to be available within PATH

steps
- recurse all sub folders (sf)
- transfer source sf/*.wav to destination sf/*.mp3
    - if destination sf/*.mp3 does not exist
    - if source sf/*.wav is newer
    - if force overwrite -f is specified

usage: this script [options] <source folder> <destination folder>
options
    -q  <quality> medium standard extreme insane or <kbps>
        default: hifi (recommended)
        kbps: 32 40 48 56 64 80 96 112 128 160 192 224 256 320
    -f  force overwrite existing mp3 files
        default: overwrites if wav is newer
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
from ff import FF_XGlob
from mtbase import MtBase
from progress import ProgressNum
from stopWatch import StopWatch
from toType import toInt, toBool



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

    def scanWav(self, rootWav):
        glWav = FF_XGlob(rootWav, '(*).wav')
        self.dataWav = tuple(d for d in glWav)

    def scanMp3(self, rootMp3):
        glMp3 = FF_XGlob(rootMp3, '(*).mp3')
        self.mapMp3 = { deMp3.rp:deMp3.fs for deMp3 in glMp3 }


    @staticmethod
    def mDir(dir):
        if isfile(dir): remove(dir)
        makedirs(dir, exist_ok=True)

    def outLimit(self):
        return self.limit and self.cnt >= self.limit

    def w2m(self, wav:str, mp3:str):
        if isdir(mp3): rmtree(mp3)
        res = system(f'{self.cmd} "{wav}" "{mp3}"')
        if res == 0:
            self.cnt.proceed()
        else:
            self.errors += 1

    def process(self, workload:list):
        # print('process:', len(workload))
        for wav, mp3 in workload:
            self.launch(self.w2m, wav, mp3)
            if self.outLimit():
                # print('limit!')
                break

    def transfer(self, rootWav:str, rootMp3:str):
        if self.chkDir(rootWav) + self.chkDir(rootMp3) > 0:
            exit(1)
        self.cnt.reset()
        sw = StopWatch()
        self.errors = 0

        glWav = FF_XGlob(rootWav, '(*).wav')
        glMp3 = FF_XGlob(rootMp3, '(*).mp3')

        self.launch(self.scanWav, rootWav)
        self.launch(self.scanMp3, rootMp3)
        # dataWav = tuple(d for d in glWav)
        # mapMp3 = { deMp3.rp:deMp3.fs for deMp3 in glMp3 }
        self.finalize()

        sw.stop()
        self.info('analysis', sw.str_sec())

        for deWav in self.dataWav:
            fsMp3 = self.mapMp3.get(deWav.rp)
            workload = []
            if fsMp3:
                # print('matched:', deWav.rp )
                mMp3 = { key:fe for key, fe in fsMp3 }
                # print('mMp3', len(mMp3))
                for keyWav, feWav in deWav.fs:
                    feMp3 = mMp3.get(keyWav)
                    if feMp3:
                        # print('found:', feMp3.path)
                        if self.force or feWav.stat().st_mtime > feMp3.stat().st_mtime:
                            workload.append((feWav.path, feMp3.path))
                            # print('C1', feWav.path, '->', feMp3.path)
                    else:
                        pathMp3 = join(rootMp3, deWav.rp, f'{keyWav}.mp3')
                        # print('C2:', feWav.path, '->', pathMp3)
                        workload.append((feWav.path, pathMp3))
            else:
                dirMp3 = join(rootMp3, deWav.rp)
                # print('check dir:', dirMp3)
                self.mDir(dirMp3)
                for keyWav, feWav in deWav.fs:
                    pathMp3 = join(dirMp3, f'{keyWav}.mp3')
                    # print('C3:', feWav.path, '->', pathMp3)
                    workload.append((feWav.path, pathMp3))

            self.process(workload)
            if self.outLimit(): break

        self.finalize()

        print()
        sw.stop()
        self.info('errors', self.errors)
        self.info('elapsed time', sw.str_sec())
        self.info('average', sw.avrg_str_sec(self.cnt.count()))

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    converter = Wav2Mp3(quality=opts['q'], force=opts['f'], limit=opts['l'], numThreads=opts['t'])

    while len(args) > 1:
        converter.transfer(*args[0:2])
        args = args[2:]
