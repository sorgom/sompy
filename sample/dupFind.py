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
                reg[fe.name()].append(fe)

        print('analysis..')
        cnt_name = 0
        cnt_size = 0
        cnt_hash = 0

        for fn, fs in reg.items():
            pw.proceed()
            # more two or more files with same name
            if len(fs) > 1:
                cnt_name += len(fs) - 1
                # check for same file size
                hs = defaultdict(list)
                for fe in fs:
                    hs[fe.stat().st_size].append(fe)
                for ls in hs.values():
                    if len(ls) > 1:
                        cnt_size += len(ls) - 1
                        # check for same file checksum
                        hh = defaultdict(list)
                        for es in ls:
                            hh[self.hash(es)].append(es)
                            for lh in hh.values():
                                if len(lh) > 1:
                                    cnt_hash += len(lh) - 1
                                    print(f'> {fn}', *(eh.path() for eh in lh), sep="\n- ")

        print(f'name duplicates:{cnt_name:>6}')
        print(f'size duplicates:{cnt_size:>6}')
        print(f'hash duplicates:{cnt_hash:>6}')

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    df = dupFind()

    if len(args) > 0:
        df.scan(*args[0:1])
