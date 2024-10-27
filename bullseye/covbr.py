"""
clean covbr reports from fully covered files

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
    def __init__(self, doc=__doc__) -> None:
        self.rFile = r'\w+(?:/\w+)*\.(?:cpp|h):'
        self.rEclip = r'(?: +\.\.\.\n)?'
        self.rxDouble = re.compile(rf'^{self.rEclip}(?:{self.rFile}\n)*({self.rFile})', re.M)
        self.rxTail = re.compile(rf'{self.rEclip}(?:{self.rFile})?\s*$')
        self.rxSpc = re.compile(rf'\s+(\n{self.rFile})')
        self.doc = doc
        self.postFunc = None
        self.opts = {}

    def process(self, fp:str):
        with open(fp, 'r') as fh:
            cont = fh.read()
            fh.close()
            newc = re.sub(r'\s+$', '', 
                self.rxTail.sub('', 
                    self.rxSpc.sub(r'\n\1', 
                        self.rxDouble.sub(r'\n\1', cont.replace('\r', ''))))) + '\n'
            if self.postFunc:
                self.postFunc(fp, newc)
            elif newc != cont:
                print('->', fp)
                with open(fp, 'w') as fh:
                    fh.write(newc)
                    fh.close()

    def processDir(self, dir:str, pattern:str):
        cdir = getcwd()
        chdir(dir)
        for fp in glob(pattern):
            self.process(fp)
        chdir(cdir)

    def processCLI(self):
        opts, args = docOpts(self.doc, reqArgs=True)
        self.opts = opts
        for arg in args:
            if isfile(arg):
                self.process(arg)
            elif isdir(arg):
                self.processDir(arg, opts.get('g', 'todo_*.txt'))
            else:
                print(f'"{arg}" is neither a file nor a directory')

if __name__ == '__main__':
    Covbr().processCLI()

