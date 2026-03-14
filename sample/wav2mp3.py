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
"""
import sompy
from convertBase import ConvertBase

class Wav2Mp3(ConvertBase):
    "the wav2mp3 class"

    def __init__(self, quality=None, force=None, limit=None, clean=None, numThreads=None):
        super().__init__('lame', 'wav', 'mp3', force, limit, clean, numThreads)
        if quality:
            if quality in 'medium standard extreme insane 32 40 48 56 64 80 96 112 128 160 192 224 256 320':
                pass
            else:
                print('unsuitable quality:', quality)
                exit(1)
        else:
            quality = 'hifi'

        self.cmd = f'{self.bin} --quiet --preset {quality}'

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    wav2mp3 = Wav2Mp3(quality=opts['q'], force=opts['f'], limit=opts['l'], numThreads=opts['t'])

    while len(args) > 1:
        wav2mp3.transfer(*args[0:2])
        args = args[2:]
