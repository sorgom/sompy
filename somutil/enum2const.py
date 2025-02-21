import re
from sys import argv

rxEnum = re.compile(r'^( *)enum +(\w+)(?: [^\r\n]*)?(?:\r?\n\1)?\{\r?\n(.*?)\r?\n\1\}', re.M | re.S)

rxValue = re.compile(r'^ *(\w+)(?: *= *(?:(\d+)|(\w+)))?', re.M)


def prVal(ind:str, nm:str, val:int, ref:str):
    print(f'{ind}static const UINT8 {nm} = {ref if ref else val}')

def txt2const(cont:str):
    vmap = {}
    for me in rxEnum.findall(cont):
        ind, ne, ce = me
        print(f'{ind}// enum {ne}')
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
