"""
find duplicate files

usage1: this script -s folder [options]
usage2: this script -i
options
    -s  <folder> scan folder
    -i  interactively process scan results
    -f  <file> use xglobs from file for scan
    -b  <file> binary scan results storage file
    -p  preview only
    -h  this help
"""
from collections import defaultdict
from hashlib import file_digest, new as new_hash
from os import remove, stat
from os.path import dirname, basename, join, abspath
from pickle import dump as pdump, load as pload
from sys import stderr
import re

import sompy
from ff import FF_XGlob
from progress import ProgressPercent
from dirTools import chkFile, chkDir
from formats import humanbytes

class dupFind():
    "the duplicate finder class"

    def __init__(self, hashType:str='sha1'):
        self.fhash = lambda fh: file_digest(fh, hashType).hexdigest()
        self.newhash = lambda : new_hash(hashType)

    def checksum(self, fe):
        try:
            with open(fe.path(), 'rb') as fh:
                return '.'.join((self.fhash(fh), fe.name()))
        except:
            return None

    @staticmethod
    def pklName(fname=None):
        if fname is None:
            return f'{__file__}.pkl'
        fname = re.sub(r'^(.*)\.pkl', r'\1', fname, flags=re.I)
        return abspath(f'{fname}.pkl')

    @staticmethod
    def info(what, cont=''):
        print(f'{what:<20}: {cont:>10}', file=stderr)

    @staticmethod
    def prevRm(dir, files):
        print(dir, *files, sep="\n- ")

    @staticmethod
    def execRm(dir, files):
        for fn in files:
            remove(join(dir, fn))

    def loadPkl(self, pkl):
        with open(pkl, 'rb') as fh:
            (self.hDirs, self.hDirChecksums, self.hChecksum) = pload(fh)

    def dumpPkl(self, pkl):
        with open(pkl, 'wb') as fh:
            pdump((self.hDirs, self.hDirChecksums, self.hChecksum), fh)


    def scan(self, root:str, xglobFile=None, pkl=None):
        try:
            ff = FF_XGlob(root, xglobFile=xglobFile)
            pkl = self.pklName(pkl)
            chkDir(dirname(pkl))
        except Exception as e:
            print(e)
            return

        reg = defaultdict(list)

        self.info('ROOT:', ff.root())

        self.info('scan', '...')

        for de in ff:
            for fe in de.data:
                reg[fe.name()].append(fe)

        # folder -> { folders with common files }
        # path -> { paths, ... }
        self.hDirs = defaultdict(set)

        # folder -> { file checksums }
        # path -> { checksum, .... }
        self.hDirChecksums = defaultdict(set)

        # check sum  -> file name
        # checksum -> basename fo file
        # must be checked for duplicate checksum
        self.hChecksum = dict()

        pp = ProgressPercent(len(reg))

        self.info('analysis', '...')
        cnt_name = 0
        cnt_size = 0
        cnt_csum = 0
        cnt_byte = 0

        for fn, ln in reg.items():
            if len(ln) < 2: continue
            pp.proceed()
            cnt_name += len(ln)
            #   separate into file size
            hs = defaultdict(list)
            for en in ln:
                hs[en.stat().st_size].append(en)
            #   filter entries with less than 2
            for sz, ls in hs.items():
                if len(ls) < 2: continue
                cnt_size += len(ls)
                #   separate into checksum identity
                hc = defaultdict(list)
                for es in ls:
                    cs = self.checksum(es)
                    cnt_byte += sz
                    if cs is None: continue
                    hc[cs].append(es)
                for cs, lc in hc.items():
                    if len(lc) < 2: continue
                    cnt_csum += len(lc)
                    self.hChecksum[cs] = fn
                    dirs = list()
                    for ec in lc:
                        dir = dirname(ec.path())
                        self.hDirChecksums[dir].add(cs)
                        dirs.append(dir)
                    for n, dir in enumerate(sorted(dirs)):
                        for dir2 in dirs[n + 1:]:
                            if dir2 != dir:
                                self.hDirs[dir].add(dir2)


        self.dumpPkl(pkl)

        self.info('name duplicates', cnt_name)
        self.info('size duplicates', cnt_size)
        self.info('hash duplicates', cnt_csum)
        self.info('bytes hashed', humanbytes(cnt_byte))

    def interact(self, pkl=None, preview=None):
        """process scan data"""
        try:
            pkl = self.pklName(pkl)
            chkFile(pkl)
        except Exception as e:
            print(e)
            return

        if preview:
            rm = lambda *p : self.prevRm(*p)
        else:
            rm = lambda *p : self.execRm(*p)

        self.loadPkl(pkl)

        chg = False

        for dir1, others in sorted(self.hDirs.items()):
            s1 = self.hDirChecksums[dir1]
            for dir2 in others:
                s2 = self.hDirChecksums[dir2]
                sc = s1 & s2
                if not sc: continue
                fs = tuple(self.hChecksum[cs] for cs in sc)
                dirs = (dir1, dir2)
                while True:
                    print()
                    print(len(fs), 'common files')
                    print(*fs)
                    for n, dir in enumerate(dirs):
                        print(f'{n+1}) {dir} ')
                    print('select number to KEEP (enter: skip, x: exit): ', end='')
                    nClear = None
                    c = input()
                    if c.isdigit():
                        n = int(c)
                        if n > 0 and n <= 2:
                            nClear = n % 2
                            break
                        else: continue
                    elif c and c in 'xXqQ':
                        print('exit')
                        return
                    else:
                        print()
                        break
                if nClear is not None:
                    dc = dirs[nClear]
                    self.hDirChecksums[dc] -= sc
                    rm(dc, fs)
                    chg = True

        if chg and not preview:
            self.dumpPkl(pkl)

if __name__ == '__main__':
    from docopts import docopts, dochelp

    opts, args = docopts(__doc__, all=True)

    df = dupFind()

    if opts['s']:
        df.scan(opts['s'], xglobFile=opts['f'], pkl=opts['b'])
    elif opts['i']:
        df.interact(*args, pkl=opts['b'], preview=opts['p'])
    else:
        dochelp(__doc__)
