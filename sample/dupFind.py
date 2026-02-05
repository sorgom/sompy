"""
find duplicate files

usage: this script options
options
    -s  <folder> scan folder
    -p  <file> process scan results text file
        -a <rel path> auto prefer path
    -h  this help
"""
from collections import defaultdict
from hashlib import file_digest, new as new_hash
from os.path import dirname, join
import re

import sompy
from ff import FF_Base, FF_Re
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

    def scan(self, root:str, auto=None):
        try:
            ff = FF_Base(root)
        except Exception as e:
            print(e)
            return

        ff.addCheckXD(lambda de : de.name() in ['git', '.git', 'Adobe', 'installers', '$RECYCLE.BIN', 'MyDownloads'])
        ff.addCheckXF(lambda fe : fe.name() in ['id_rsa', 'id_rsa.pub', 'known_hosts', 'index.html', 'index.htm', 'index.php', 'desktop.ini'])

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

    def analyze(self, fp):
        """process text report"""
        try:
            with open(fp, 'r') as fh:
                cont = fh.read()
        except Exception as e:
            print(e)

        def dirHash(dirs:tuple):
            h = self.newhash()
            for d in dirs: h.update(d.encode('utf-8'))
            return h.hexdigest()

        rxFile  = re.compile(r'^> (.+)((?:\n- .+)+)', re.M)
        rxPaths = re.compile(r'^- (.+)', re.M)
        hDirFiles = defaultdict(set)
        hDirCombis = dict()

        for fn, cpaths in rxFile.findall(cont):
            dirs = tuple(sorted(dirname(p) for p in rxPaths.findall(cpaths)))
            hash = dirHash(dirs)
            if hash not in hDirCombis:
                hDirCombis[hash] = dirs
            for dir in dirs:
                hDirFiles[dir].add(fn)

        def askCombi(combi:tuple):
            # list non empty folders of combi
            choice = tuple((dir, files) for dir, files in [(dir, hDirFiles[dir]) for dir in combi] if files)
            if len(choice) < 2: return
            files = tuple(hDirFiles[dir] for dir in combi)
            # check if files left
            s = None
            while True:
                print(f'Nr: {"files":<5}: in folder:')
                for n, (dir, files) in enumerate(choice):
                    print(f'{n+1:>2}: {len(files):>5}: {dir}')
                print('select number to keep or enter to skip: ', end='')
                c = input()
                if c.isdigit():
                    n = int(c)
                    if n > 0 and n <= len(choice):
                        s = n - 1
                        break
                    else: continue
                elif c and c in 'xX':
                    print('exit')
                    exit()
                else:
                    print()
                    break
            if s is None: return
            print('selected:', s)
            sk = choice[s][1]
            for n, (dir, files) in enumerate(choice):
                if n != s:
                    common = sk & files
                    for fn in common:
                        fp = join(dir, fn)
                        print('remove', fp )
                    hDirFiles[dir] -= common

            for dir, files in choice:
                print(len(hDirFiles[dir]), dir)


        for combi in hDirCombis.values():
            askCombi(combi)

        print('dirs  :', len(hDirFiles))
        print('combis:', len(hDirCombis))

if __name__ == '__main__':
    from docopts import docopts, dochelp

    opts, args = docopts(__doc__, all=True)

    df = dupFind()

    if opts['s']:
        df.scan(opts['s'])
    elif opts['p']:
        df.analyze(opts['p'])
    else:
        dochelp(__doc__)
