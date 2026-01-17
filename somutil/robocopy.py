from os import walk, remove
from os.path import relpath, join, isdir, isfile, getmtime
from shutil import rmtree, copytree, copyfile, copystat
import re

class Robo(object):
    "robo copier class"
    def __init__(self, verbose=False):
        self.verbose = verbose
        #   no directory in target
        self.rxNoDir    = re.compile(r'^(?:__pycache__)$')
        #   generally ignored
        self.rxIgDir    = re.compile(r'^(?:System Volume Information|\$.*)$')
        #   no file in target
        self.rxNoFile   = re.compile(r'^(?:)$')

    @staticmethod
    def rpath(dir:str, base:str):
        "relative path without ."
        rp = relpath(dir, base)
        return '' if rp == '.' else rp

    def chkDir(self, dir):
        ok = isdir(dir)
        self.echo('OK :' if ok else 'NOK:', dir)
        return ok

    def echo(self, *args):
        "print if verbose"
        if self.verbose: print(*args)


    def cpfile(self, src:str, dst:str):
        "copy file with attributes"
        self.echo('copy:', dst)
        try:
            copyfile(src, dst)
            copystat(src, dst)
        except:
            pass

    def rmfile(self, file:str, reason:str):
        "remove a file for given reason"
        self.echo(f'rm ({reason}):', file)
        remove(file)

    def cpdir(self, src:str, dst:str):
        "copy directory"
        self.echo('copy dir:', dst)
        try:
            copytree(src, dst)
        except:
            pass

    def rmdir(self, dir:str, reason:str):
        "remove directory"
        self.echo(f'rm dir ({reason}):', dir)
        rmtree(dir)

    def isOkDir(self, dir:str, all:bool=False):
        "determine whether to list a directory"
        return (not self.rxIgDir.match(dir)) and (all or not self.rxNoDir.match(dir))

    def wlist(self, dir:str, all:bool=False):
        "list relative non empty directories with files and subdirs"
        self.echo('reading', dir, '..')
        return [ [self.rpath(root, dir), files] for root, dirs, files in walk(dir) if self.isOkDir(root, all) and (files or dirs)]

    def copy(self, src:str, dst:str):
        if not (self.chkDir(src) and self.chkDir(dst)):
            print('skip:', src, dst)
            return

        ls = self.wlist(src)
        ld = self.wlist(dst, True)
        ds = { dir:files for dir, files in ls }

        print('src:', len(ls))
        print('dst:', len(ld))

        # removal in target
        for dir, tfiles in ld:
            ddir = join(dst, dir)
            # already removed?
            if not isdir(ddir): continue
            sfiles = ds.get(dir, None)
            # non source folder
            if sfiles is None:
                self.rmdir(ddir, 'ns')
                continue
            for file in tfiles:
                dfile = join(ddir, file)
                # non source file
                if not file in sfiles:
                    self.rmfile(dfile, 'ns')
                    continue
                # source is newer
                sfile = join(src, dir, file)
                try:
                    ts = getmtime(sfile)
                    td = getmtime(dfile)
                    if ts > td:
                        self.rmfile(dfile, 'mt')
                except:
                    pass

        # copy from source to target
        for dir, sfiles in ls:
            ddir = join(dst, dir)
            sdir = join(src, dir)
            if isfile(ddir):
                self.rmfile(ddir, 'if')

            if not isdir(ddir):
                self.cpdir(sdir, ddir)
                continue
            for file in sfiles:
                sfile = join(sdir, file)
                dfile = join(ddir, file)
                if isdir(dfile):
                    self.rmdir(dfile, 'fd')
                if not isfile(dfile):
                    self.cpfile(sfile, dfile)

if __name__ == '__main__':
    robo = Robo(True)
#    robo.copy('C:/users/MS/data', 'M:/tmp_backup_test')
    robo.copy('M:', 'N:')
