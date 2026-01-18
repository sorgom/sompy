"""
a simple robocopy style script
usage: python this script [options] <source folder> <target folder>
options:
    -v  verbose
    -D  <skip folders patterns> comma separated
    -F  <skip files   patterns> comma separated
    -h  this help
"""
from collections import Counter
from datetime import datetime
from os import walk, remove
from os.path import relpath, join, isdir, getmtime, basename
from shutil import rmtree, copytree, copyfile, copystat
import re

class Robo(object):
    "robo copier class"
    def __init__(self, verbose=False, xDirs=None, xFiles=None):
        self.verbose = verbose
        #   no directory copy to destination
        self.rxNoDir = self.glob2re('__pycache__|found???', xDirs)
        # print('pattern:', self.rxNoDir.pattern)
        # exit()
        #   generally ignored
        self.rxIgDir    = re.compile(r'^(?:System Volume Information|\$.*)$')
        #   no file copy to destination
        self.rxNoFile   = re.compile(r'^(?:)$')

        self.stats = Counter()

        self.caps = ['files removed', 'files copied', 'folders removed', 'folders copied', 'exceptions']

    @staticmethod
    def glob2re(x:str, usr:str):
        if usr:
            x += f'|{usr}'
        x = re.sub(r'\?', '.', re.sub(r'\*', '.*', x))
        return re.compile(rf'(?:^|[:/\\])(?:{x})(?:[/\\]|$)')

    @staticmethod
    def rpath(dir:str, base:str):
        "relative path without ."
        rp = relpath(dir, base)
        return '' if rp == '.' else rp

    def chkDir(self, dir):
        "check if folder exists"
        ok = isdir(dir)
        if ok:
            if self.verbose:
                self.info('OK', dir)
        else:
            self.info('NOK', dir)
        return ok

    def echo(self, *args):
        "print if verbose"
        if self.verbose: print(*args)

    @staticmethod
    def info(top, cont):
        print(f'{top:<20}:{cont:>10}')

    @staticmethod
    def rmn(a:list, n:int):
        del(a[n:n+1])

    def rmfile(self, file:str, reason:str):
        "remove a file for given reason"
        self.echo(f'rm ({reason}):', file)
        remove(file)
        self.stats[0] += 1

    def cpfile(self, src:str, dst:str):
        "copy file with attributes"
        self.echo('copy:', dst)
        self.stats[1] += 1
        try:
            copyfile(src, dst)
            copystat(src, dst)
        except:
            self.exc()


    def rmdir(self, dir:str, reason:str):
        "remove directory"
        self.echo(f'rm dir ({reason}):', dir)
        self.stats[2] += 1
        try:
            rmtree(dir)
        except Exception as x:
            print(x)
            self.exc()

    def cpdir(self, src:str, dst:str):
        "copy directory"
        self.echo('copy dir:', dst)
        try:
            copytree(src, dst)
        except:
            self.exc()
        self.stats[3] += 1

    def isOkDir(self, dir:str, all:bool=False):
        "determine whether to list a directory"
        return (not self.rxIgDir.search(dir)) and (all or not self.rxNoDir.search(dir))

    def wlist(self, dir:str, all:bool=False):
        "list relative non empty directories with files and subdirs"
        self.echo('reading', dir, '..')
        return [ [self.rpath(root, dir), files] for root, dirs, files in walk(dir) if self.isOkDir(root, all) and (files or dirs)]

    def exc(self):
        self.stats[4] += 1

    def showStats(self):

        print()
        for n, c in enumerate(self.caps):
            self.info(c, self.stats[n])

        print()
        c = re.sub(r'\..*', '' , str(datetime.now() - self.start))
        self.info('elapsed', c)


    def copy(self, src:str, dst:str):
        print()
        self.info('source', src)
        self.info('destination', dst)
        if not (self.chkDir(src) and self.chkDir(dst)):
            print('SKIPPED')
            return

        self.start = datetime.now()

        print('...', end="\r")

        ls = self.wlist(src)
        ld = self.wlist(dst, True)
        ds = { dir:files for dir, files in ls }

        print('     ')

        self.echo('src:', len(ls))
        self.echo('dst:', len(ld))

        self.stats = Counter()

        # removal in target
        lnd = list(range(0, len(ld)))
        lnd.reverse()

        for nd in lnd:
            dir, dfs = ld[nd]
            ddir = join(dst, dir)
            sfs = ds.get(dir, None)
            # non source folder
            if sfs is None:
                self.rmdir(ddir, 'ns')
                self.rmn(ld, nd)
                continue
            lnf = list(range(0, len(dfs)))
            lnf.reverse()
            for nf in lnf:
                file = dfs[nf]
                dfile = join(ddir, file)
                # non source file
                if not file in sfs:
                    self.rmn(dfs, nf)
                    self.rmfile(dfile, 'ns')
                    continue
                # source is newer
                sfile = join(src, dir, file)
                try:
                    ts = getmtime(sfile)
                    td = getmtime(dfile)
                    if ts > td:
                        self.rmn(dfs, nf)
                        self.rmfile(dfile, 'mt')
                except:
                    self.exc()
                    self.rmn(dfs, nf)
                    self.rmfile(dfile, 'ex')

        # copy from source to target
        dd = { dir:files for dir, files in ld }
        for dir, sfs in ls:
            ddir = join(dst, dir)
            sdir = join(src, dir)
            dfs = dd.get(dir, None)
            if dfs is None:
                if not isdir(ddir):
                    self.cpdir(sdir, ddir)
                continue
            for file in sfs:
                if not file in dfs:
                    sfile = join(sdir, file)
                    dfile = join(ddir, file)
                    self.cpfile(sfile, dfile)
        self.showStats()

if __name__ == '__main__':
    from docopts import docopts
    opts, args = docopts(__doc__, reqArgs=True)
    robo = Robo(True, xDirs=opts.get('D', ''), xFiles=opts.get('F', ''))
    while len(args) > 1:
        robo.copy(args.pop(0), args.pop(0))
