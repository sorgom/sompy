"""
find duplicate files

usage1: this script -s folder [options]
usage2: this script -i
options
    -s  <folder> scan folder
    -i  interactively process scan results
    -f  <file> use xglobs from file for scan
    -b  <file> binary scan results storage file
    -h  this help
"""
from collections import defaultdict
from hashlib import file_digest, new as new_hash
from os.path import dirname, join, abspath
from pickle import dump as pdump, load as pload
import re

import sompy
from ff import FF_XGlob
from progress import ProgressPercent
from dirTools import chkFile, chkDir

class dupFind():
    "the duplicate finder class"

    def __init__(self, hashType:str='sha1'):
        self.fhash = lambda fh: file_digest(fh, hashType).hexdigest()
        self.newhash = lambda : new_hash(hashType)
        pass

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

    def scan(self, root:str, xglobFile=None, pklOut=None):
        try:
            ff = FF_XGlob(root, xglobFile=xglobFile)
            pklOut = self.pklName(pklOut)
            chkDir(dirname(pklOut))
        except Exception as e:
            print(e)
            return

        reg = defaultdict(list)

        print('ROOT:', ff.root())

        print('scan..')

        for de in ff:
            for fe in de.data:
                reg[fe.name()].append(fe)

        # folder -> { folders with common files }
        # path -> { paths, ... }
        hDirs = defaultdict(set)

        # folder -> { file checksums }
        # path -> { checksum, .... }
        hDirChecksums = defaultdict(set)

        # check sum  -> file name
        # checksum -> basename fo file
        # must be checked for duplicate checksum
        hChecksum = dict()


        pp = ProgressPercent(len(reg))

        print('analysis..')
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
                    hChecksum[cs] = lc[0].name()
                    dirs = list()
                    for ec in lc:
                        dir = dirname(ec.path())
                        hDirChecksums[dir].add(cs)
                        dirs.append(dir)
                    for n, dir in enumerate(sorted(dirs)):
                        for dir2 in dirs[n + 1:]:
                            hDirs[dir].add(dir2)

        print('writing', pklOut)
        with open(pklOut, 'wb') as fh:
            pdump((hDirs, hDirChecksums, hChecksum), fh)


        print(f'name duplicates:{cnt_name:>6}')
        print(f'size duplicates:{cnt_size:>6}')
        print(f'hash duplicates:{cnt_csum:>6}')
        print(f'bytes hashed   :{cnt_byte:>6}')

        return




        return

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
                                cnt_csum += len(lh) - 1
                                print(f'> {fn}', *(eh.path() for eh in lh), sep="\n- ")

        print(f'name duplicates:{cnt_name:>6}')
        print(f'size duplicates:{cnt_size:>6}')
        print(f'hash duplicates:{cnt_csum:>6}')
        print(f'bytes hashed   :{cnt_byte:>6}')

    def interact(self, pklIn=None):
        """process scan data"""
        try:
            pklIn = self.pklName(pklIn)
            chkFile(pklIn)
        except Exception as e:
            print(e)
            return

        with open(pklIn, 'rb') as fh:
            (hDirs, hDirChecksums, hChecksum) = pload(fh)

        print('loaded:', len(hDirs), len(hDirChecksums), len(hChecksum))

        for dir1, others in hDirs.items():
            s1 = hDirChecksums[dir1]
            for dir2 in others:
                s2 = hDirChecksums[dir2]
                sc = s1 & s2
                if not sc: continue
                fs = tuple(hChecksum[cs] for cs in sc)
                dirs = (dir1, dir2)
                while True:
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
                    elif c and c in 'xX':
                        print('exit')
                        return
                    else:
                        print()
                        break
                if nClear is not None:
                    dc = dirs[nClear]
                    hDirChecksums[dc] -= sc
                    print('clear:', dirs[nClear])
                    for fn in fs:
                        fp = join(dc, fn)
                        print('remove:', fp)


        # rxPref = None

        # if prefPaths:
        #     rxPref = re.compile(r'^(?:' + '|'.join(map(re.escape, prefPaths)) + r').*$')
        #     print('pref:', rxPref.pattern)

        # def dirHash(dirs:tuple):
        #     h = self.newhash()
        #     for d in dirs: h.update(d.encode('utf-8'))
        #     return h.hexdigest()

        # rxFile      = re.compile(r'^> (.+)((?:\n- .+)+)', re.M)
        # rxPaths     = re.compile(r'^- (.+)', re.M)
        # hDirFiles   = defaultdict(set)
        # hDirCombis  = dict()
        # reducedDirs = set()

        # for fn, cpaths in rxFile.findall(cont):
        #     dirs = tuple(sorted(dirname(p) for p in rxPaths.findall(cpaths)))
        #     hash = dirHash(dirs)
        #     if hash not in hDirCombis:
        #         hDirCombis[hash] = dirs
        #     for dir in dirs:
        #         hDirFiles[dir].add(fn)

        # def reduceCombi(choice:tuple, nClear):
        #     sk = choice[nClear][1]
        #     for n, (dir, files) in enumerate(choice):
        #         if n != nClear:
        #             common = sk & files
        #             for fn in common:
        #                 fp = join(dir, fn)
        #                 print('remove', fp )
        #             hDirFiles[dir] -= common
        #             reducedDirs.add(dir)

        # def askChoice(choice:tuple):
        #     nClear = None
        #     while True:
        #         print(f'Nr: {"files":<5}: in folder:')
        #         for n, (dir, files) in enumerate(choice):
        #             print(f'{n+1:>2}: {len(files):>5}: {dir}')
        #         print('select number to keep (enter: skip, x: exit): ', end='')
        #         c = input()
        #         if c.isdigit():
        #             n = int(c)
        #             if n > 0 and n <= len(choice):
        #                 nClear = n - 1
        #                 break
        #             else: continue
        #         elif c and c in 'xX':
        #             print('exit')
        #             exit()
        #         else:
        #             print()
        #             break
        #     return nClear

        # def prefChoice(choice:tuple):
        #     res = tuple(n for n, (dir, _) in enumerate(choice) if rxPref.match(dir))
        #     return res[0] if len(res) == 1 else None

        #     # for dir, files in choice:
        #     #     print(len(hDirFiles[dir]), dir)


        # if rxPref:
        #     procChoice = lambda choice: prefChoice(choice)
        # else:
        #     procChoice = lambda choice: askChoice(choice)

        # for combi in hDirCombis.values():
        #     choice = tuple((dir, files) for dir, files in [(dir, hDirFiles[dir]) for dir in combi] if files)
        #     if len(choice) > 1:
        #         n = procChoice(choice)
        #         if n is not None: reduceCombi(choice, n)

        # for dir in sorted(reducedDirs):
        #     files = hDirFiles[dir]
        #     if len(files) > 0:
        #         print(dir, *files)


        # print('dirs  :', len(hDirFiles))
        # print('combis:', len(hDirCombis))

if __name__ == '__main__':
    from docopts import docopts, dochelp

    opts, args = docopts(__doc__, all=True)

    df = dupFind()

    if opts['s']:
        df.scan(opts['s'], xglobFile=opts['f'], pklOut=opts['b'])
    elif opts['i']:
        df.interact(*args, pklIn=opts['b'])
    else:
        dochelp(__doc__)
