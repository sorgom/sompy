import re
from sys import argv

rCom = r'^( *//[^\n*]\n)?'
rxEnum = re.compile(
    r'^( *//[^\n]*\n)?' +
    r'( *)(enum +\w+.*)(?:\r?\n\2)?\{\r?\n([^\}]*)\r?\n\2\}', re.M)

rxValue = re.compile(r'^ *(\w+)(?: *= *(?:(\d+)|(\w+)))?', re.M)


def prVal(ind:str, nm:str, val:int, ref:str):
    print(f'{ind}static const UINT8 {nm} = {ref if ref else val};')

def txt2const(cont:str):
    vmap = {}
    for me in rxEnum.findall(cont):
        com, ind, ne, ce = me
        if com:
            print(com, end='')
        print(f'{ind}//  was: enum {ne}')
        curv = 0
        for mv in rxValue.findall(ce):
            nm, val, ref = mv
            if ref:
                curv = vmap[ref]
            elif val:
                curv = int(val)
            vmap[nm] = curv
            prVal(ind, nm, curv, ref)
            curv += 1
        print()

def fp2const(fp:str):
    with open(fp) as fh:
        txt2const(fh.read())

if __name__ == "__main__":
    for fp in argv[1:]:
        fp2const(fp)
