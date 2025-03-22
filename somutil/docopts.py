"""
simple getopt and help utility
- reads options from (preferably __doc__) string
- returns options dict and arguments
- exits with help if option "h" is given

Sample options in doc string:
-s  a switch option
-f  <some> a value option

Help output:
replaces "__file__" and "this script" with script name
"""
# author SOM, Manfred Sorgo

from getopt import getopt
from sys import argv, stderr
from os.path import basename
from os import name as osname
import re

def toErr(*args):
    print(*args, file=stderr)

def docrep(doc:str):
    """replace "__file__" and "this script" in doc string"""
    rxRep = re.compile(r'\b(?:__file__|this ?script)\b', re.I)
    sub = basename(argv[0])
    return rxRep.sub(sub, doc).strip()

def dochelp(doc:str, ret:int=0):
    """print doc string as help and exit"""
    print(f'\n{docrep(doc)}\n')
    exit(ret)

def docopts(doc:str, args:list=argv[1:], help=True, reqArgs=False, all=False) -> tuple[dict, list]:
    """parse options from doc string and command line"""
    rxOpt = re.compile(r'^ *-([a-zA-Z])( +<.+?>)?', re.M)
    res = {}
    ostr = ''
    isVal = {}
    keys = set()
    for mo in rxOpt.finditer(doc):
        key = mo.group(1)
        if key in keys:
            toErr(f'duplicate option -{key}')
            exit(1)
        keys.add(key)
        ostr += key
        if mo.group(2):
            ostr += ':'
            isVal[key] = True

    try:
        opts, args = getopt(args, ostr)
    except Exception as e:
        toErr(e)
        exit(1)
    if reqArgs and not args:
        dochelp(doc)
    for o, v in opts:
        key = o[1]
        if help and key == 'h':
            dochelp(doc)
        res[key] = v if isVal.get(key) else True

    if all:
        for key in keys:
            if key not in res:
                res[key] = None if isVal.get(key) else False

    return res, args

if __name__ == '__main__':
    def docshell():
        """docopts to shell"""
        if len(argv) < 2: return
        txt = argv[1]
        with open(txt) as f:
            opts, args = docopts(f.read(), args=argv[2:], help=False, all=True)

        cfunc = lambda c: c
        cTrue = 'true'
        cFalse = 'false'
        cpref = 'export'
        cargs = '"'

        if osname == 'nt':
            cfunc = lambda c: c + 'u' if c.isupper() else c
            cTrue = '1==1'
            cFalse = '0==1'
            cpref = 'set'
            cargs = ''

        vfunc = lambda b: cTrue if b == True else cFalse if b == False else '' if b is None  else b

        for k, v in opts.items():
            print(f'{cpref} _{cfunc(k)}={vfunc(v)}')
        print(f"{cpref} _args={cargs}{' '.join(args)}{cargs}")

    docshell()
