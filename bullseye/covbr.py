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

rFile = r'\w+(?:/\w+)*\.(?:cpp|h):'
rEclip = r'(?: +\.\.\.\n)?'
rxDouble = re.compile(rf'^{rEclip}(?:{rFile}\n)*({rFile})', re.M)
rxTail = re.compile(rf'{rEclip}(?:{rFile})?\s*$')
rxSpc = re.compile(rf'\s+(\n{rFile})')

def reduceCovbr(fp:str, func=None):
    with open(fp, 'r') as fh:
        cont = fh.read()
        fh.close()
        newc = re.sub(r'\s+$', '', rxTail.sub('', rxSpc.sub(r'\n\1', rxDouble.sub(r'\n\1', cont.replace('\r', ''))))) + '\n'
        if func:
            func(fp, newc)
        elif newc != cont:
            print('->', fp)
            with open(fp, 'w') as fh:
                fh.write(newc)
                fh.close()

def reduceCovbrDir(dir:str, pattern:str, func=None):
    cdir = getcwd()
    chdir(dir)
    for fp in glob(pattern):
        reduceCovbr(fp, func)
    chdir(cdir)

def reduceCovbrCLI(func=None, doc=__doc__):
    opts, args = docOpts(doc, reqArgs=True)
    for arg in args:
        if isfile(arg):
            reduceCovbr(arg, func=func)
        elif isdir(arg):
            reduceCovbrDir(arg, opts.get('g', 'todo_*.txt'), func=func)
        else:
            print(f'"{arg}" is neither a file nor a directory')

if __name__ == '__main__':
    reduceCovbrCLI()

