"""
find duplicate files

usage: this script [options] folder
options
    -h  this help

"""
from collections import defaultdict
from hashlib import file_digest, algorithms_available
# import re

import sompy
from ff import FF_Base, FF_Re
from progress import ProgressWheel

class dupFind():
    "the duplicate finder class"

    def __init__(self, preview=None):
        pass

    @staticmethod
    def hash(fe):
        with open(fe.path(), 'rb') as fh:
            return file_digest(fh, 'sha1').hexdigest()

    def scan(self, root:str):
        try:
            ff = FF_Base(root)
        except Exception as e:
            print(e)
            return

        ff.addCheckXD(lambda de : de.name() in ['git', '.git', 'Adobe'])
        ff.addCheckXF(lambda fe : fe.name() in ['id_rsa', 'id_rsa.pub', 'known_hosts', 'index.html', 'index.htm', 'desktop.ini'])

        reg = defaultdict(list)

        pw = ProgressWheel()

        print('scan..')

        for de in ff:
            for fe in de.data:
                pw.proceed()
                reg[fe.name()].append(fe)

        print('analysis..')
        for fn, fs in reg.items():
            pw.proceed()
            if len(fs) > 1:
                hh = defaultdict(list)
                for fe in fs:
                    hh[self.hash(fe)].append(fe)
                for h, es in hh.items():
                # for es in hh.values():
                    if len(es) > 1:
                        print(fn, *(f.path() for f in es), sep="\n- ")

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    df = dupFind()

    if len(args) > 0:
        df.scan(*args[0:1])
