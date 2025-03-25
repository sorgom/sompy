"""transfer C++ 2011 enumerations to C++ 98 compatible static constants"""
import re
from sys import argv
from cleanTxt import cleanTxt

# $1: comment,
# $2: indent
# $3: enum,
# $4: base,
# $5: values
rxEnum = re.compile(
    r'^((?: *//.*\n)*)' +
    r'( *)enum +(\w+)(?: *: *(\w+))?(?:\n\2)?\{\n([^\}]*)\n\2\}', re.M)

rxValue = re.compile(r'^ *(\w+)(?: *= *(?:(\d+)|(\w+)))?', re.M)

vmap = {}

def prVal(ind:str, nm:str, base:str, val:int, ref:str):
    print(f'{ind}static const {base or 'UINT8'} {nm} = {ref if ref else val};')

def txt2const(cont:str):
    global vmap
    cont = cleanTxt(cont, tabs=4, lf=True)
    for me in rxEnum.findall(cont):
        com, ind, ne, base, ce = me
        if com:
            print(com, end='')
        print(f'{ind}//  was: enum {ne}')
        curv = 0
        for mv in rxValue.findall(ce):
            nm, val, ref = mv
            if ref and ref in vmap:
                curv = vmap[ref]
            elif val:
                curv = int(val)
            vmap[nm] = curv

            prVal(ind, nm, base, curv, ref)
            curv += 1
        print()

def fp2const(fp:str):
    with open(fp) as fh:
        txt2const(fh.read())

if __name__ == "__main__":
    from docopts import docopts
    from fglob import fglob
    help = __doc__ + """
usage: this script [options] headers
options:
-h  this help
"""
    opts, args = docopts(help)
    for arg in fglob(args):
        fp2const(arg)
