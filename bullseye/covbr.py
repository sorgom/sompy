"""
cleans covbr reports from fully covered files

Usage: this script [options] folders / files
options:
    -g  <glob> glob pattern of the report files
        default: "todo_*.txt"
    -h  help
"""

import re
from glob import glob
from os import chdir, getcwd
from os.path import isfile, isdir
import sompy
from docOpts import docOpts

class Covbr(object):
    """covbr cleaner"""
    def __init__(self, doc=__doc__) -> None:
        self.rFile = r'\w+(?:/\w+)*\.(?:cpp|h):'
        self.rEclip = r'(?: +\.\.\.\n)?'
        self.rxDouble = re.compile(rf'^{self.rEclip}(?:{self.rFile}\n)*({self.rFile})', re.M)
        self.rxTail = re.compile(rf'{self.rEclip}(?:{self.rFile})?\s*$')
        self.rxSpc = re.compile(rf'\s+(\n{self.rFile})')
        self.doc = doc
        self.opts = {}
        self.cnt = 0

    def postFunc(self, *args):
        pass
    
    def write(self, fp:str, oldc:str, newc:str):
        if newc != oldc:
            with open(fp, 'w') as fh:
                fh.write(newc)
                fh.close()
                self.cnt += 1

    def process(self, fp:str):
        """cleans the file"""
        with open(fp, 'r') as fh:
            oldc = fh.read()
            fh.close()
            newc = re.sub(r'\s+$', '', 
                self.rxTail.sub('', 
                    self.rxSpc.sub(r'\n\1', 
                        self.rxDouble.sub(r'\n\1', oldc.replace('\r', ''))))) + '\n'
            self.write(fp, oldc, newc)
            self.postFunc(fp, newc)

    def processDir(self, dir:str, pattern:str):
        """processes all files in a directory by glob pattern"""
        cdir = getcwd()
        chdir(dir)
        for fp in glob(pattern):
            self.process(fp)
        chdir(cdir)

    def processCLI(self):
        """processes command line arguments"""
        opts, args = docOpts(self.doc, reqArgs=True)
        self.opts = opts
        for arg in args:
            if isfile(arg):
                self.process(arg)
            elif isdir(arg):
                self.processDir(arg, opts.get('g', 'todo_*.txt'))
            else:
                print(f'"{arg}" is neither a file nor a directory')
        if self.cnt:
            print(f'{self.cnt} files written')

if __name__ == '__main__':
    Covbr().processCLI()

