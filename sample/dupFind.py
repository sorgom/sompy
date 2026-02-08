"""
find duplicate files

usage1: this script -s folder
usage2: this script -p file [preferred folders ...]
options
    -s  <folder> scan folder
    -p  <file> process scan results text file
    -f  <file> use xglobs from file for scan
    -h  this help
"""
from collections import defaultdict
from hashlib import file_digest, new as new_hash
from os.path import dirname, join
import re

import sompy
from ff import FF_Base, FF_Re, FF_XGlob
from progress import ProgressPercent

class dupFind():
    "the duplicate finder class"

    def __init__(self, hashType:str='sha1'):
        self.fhash = lambda fh: file_digest(fh, hashType).hexdigest()
        self.newhash = lambda : new_hash(hashType)
        pass

    def hash(self, fe):
        try:
            with open(fe.path(), 'rb') as fh:
                return self.fhash(fh)
        except:
            return None

    def scan(self, root:str, xglobFile=None):
        try:
            print('scan with:', xglobFile)
            ff = FF_XGlob(root, xglobFile=xglobFile)
        except Exception as e:
            print(e)
            return

        # ff.addCheckXD(lambda de : de.name() in ('git', 'git_old', '.git', 'Adobe', 'installers', '$RECYCLE.BIN', 'MyDownloads', 'cadul', '_Material-Sammlungen'))
        # ff.addCheckXF(lambda fe : fe.name() in ('id_rsa', 'id_rsa.pub', 'known_hosts', 'index.html', 'index.htm', 'index.php', 'desktop.ini'))

        reg = defaultdict(list)

        print('ROOT:', ff.root())

        print('scan..')

        for de in ff:
            for fe in de.data:
                reg[fe.name()].append(fe)

        pp = ProgressPercent(len(reg))

        print('analysis..')
        cnt_name = 0
        cnt_size = 0
        cnt_hash = 0
        cnt_byte = 0

        for fn, fs in reg.items():
            pp.proceed()
            # more two or more files with same name
            if len(fs) > 1:
                cnt_name += len(fs) - 1
                # check for same file size
                hs = defaultdict(list)
                for ef in fs:
                    hs[ef.stat().st_size].append(ef)
                for sz, ls in hs.items():
                    if len(ls) > 1:
                        cnt_size += len(ls) - 1
                        cnt_byte += sz * len(ls)
                        # check for same file checksum
                        hh = defaultdict(list)
                        for es in ls:
                            hh[self.hash(es)].append(es)
                        if None in hh: del hh[None]
                        for lh in hh.values():
                            if len(lh) > 1:
                                cnt_hash += len(lh) - 1
                                print(f'> {fn}', *(eh.path() for eh in lh), sep="\n- ")

        print(f'name duplicates:{cnt_name:>6}')
        print(f'size duplicates:{cnt_size:>6}')
        print(f'hash duplicates:{cnt_hash:>6}')
        print(f'bytes hashed   :{cnt_byte:>6}')

    def analyze(self, fp, *prefPaths):
        """process text report"""
        try:
            with open(fp, 'r') as fh:
                cont = fh.read()
        except Exception as e:
            print(e)

        rxPref = None

        if prefPaths:
            rxPref = re.compile(r'^(?:' + '|'.join(map(re.escape, prefPaths)) + r').*$')
            print('pref:', rxPref.pattern)

        def dirHash(dirs:tuple):
            h = self.newhash()
            for d in dirs: h.update(d.encode('utf-8'))
            return h.hexdigest()

        rxFile      = re.compile(r'^> (.+)((?:\n- .+)+)', re.M)
        rxPaths     = re.compile(r'^- (.+)', re.M)
        hDirFiles   = defaultdict(set)
        hDirCombis  = dict()
        reducedDirs = set()

        for fn, cpaths in rxFile.findall(cont):
            dirs = tuple(sorted(dirname(p) for p in rxPaths.findall(cpaths)))
            hash = dirHash(dirs)
            if hash not in hDirCombis:
                hDirCombis[hash] = dirs
            for dir in dirs:
                hDirFiles[dir].add(fn)

        def reduceCombi(choice:tuple, nKeep):
            sk = choice[nKeep][1]
            for n, (dir, files) in enumerate(choice):
                if n != nKeep:
                    common = sk & files
                    for fn in common:
                        fp = join(dir, fn)
                        print('remove', fp )
                    hDirFiles[dir] -= common
                    reducedDirs.add(dir)

        def askChoice(choice:tuple):
            nKeep = None
            while True:
                print(f'Nr: {"files":<5}: in folder:')
                for n, (dir, files) in enumerate(choice):
                    print(f'{n+1:>2}: {len(files):>5}: {dir}')
                print('select number to keep (enter: skip, x: exit): ', end='')
                c = input()
                if c.isdigit():
                    n = int(c)
                    if n > 0 and n <= len(choice):
                        nKeep = n - 1
                        break
                    else: continue
                elif c and c in 'xX':
                    print('exit')
                    exit()
                else:
                    print()
                    break
            return nKeep

        def prefChoice(choice:tuple):
            res = tuple(n for n, (dir, _) in enumerate(choice) if rxPref.match(dir))
            return res[0] if len(res) == 1 else None

            # for dir, files in choice:
            #     print(len(hDirFiles[dir]), dir)


        if rxPref:
            procChoice = lambda choice: prefChoice(choice)
        else:
            procChoice = lambda choice: askChoice(choice)

        for combi in hDirCombis.values():
            choice = tuple((dir, files) for dir, files in [(dir, hDirFiles[dir]) for dir in combi] if files)
            if len(choice) > 1:
                n = procChoice(choice)
                if n is not None: reduceCombi(choice, n)

        for dir in sorted(reducedDirs):
            files = hDirFiles[dir]
            if len(files) > 0:
                print(dir, *files)


        print('dirs  :', len(hDirFiles))
        print('combis:', len(hDirCombis))

if __name__ == '__main__':
    from docopts import docopts, dochelp

    opts, args = docopts(__doc__, all=True)

    df = dupFind()

    if opts['s']:
        df.scan(opts['s'], xglobFile=opts['f'])
    elif opts['p']:
        df.analyze(opts['p'], *args)
    else:
        dochelp(__doc__)
