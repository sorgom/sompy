"""
bulk epub to mobi conversion
requires ebook-convert executable to be available within PATH

usage: this script [options] <source folder> <destination folder>
options
    -f  force overwrite existing mobi files
        default: overwrites if epub is newer
    -l  <int> limit of conversions per source / destination
    -t  <int> number of threads
    -h  this help
"""
import sompy
from convertBase import ConvertBase

class Epub2Mobi(ConvertBase):
    "the epub to mobi class"

    def __init__(self, force=None, limit=None, clean=None, numThreads=None):
        super().__init__('ebook-convert', 'epub', 'mobi', force, limit, clean, numThreads)

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    epub2mobi = Epub2Mobi(force=opts['f'], limit=opts['l'], numThreads=opts['t'])

    while len(args) > 1:
        epub2mobi.transfer(*args[0:2])
        args = args[2:]
