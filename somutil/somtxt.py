"""files and text functions"""
#   created by Manfred Sorgo

import re

rxLin = re.compile(r'[ \t]+$', re.M)
rxEnd = re.compile(r'\s*$')

def cleanTxt(txt:str, tabs=None) -> str:
    """expand tabs and remove trailing spaces"""
    if tabs: txt = txt.expandtabs(tabs)
    return rxEnd.sub('\n', rxLin.sub('', txt))

def fileTxt(fp) -> str:
    """read file content"""
    with open(fp, 'r') as fh:
        cont = fh.read()
        fh.close()
        return cont

def cleanFileTxt(fp:str, tabs=None) -> str:
    """read file content, expand tabs, remove trailing spaces"""
    return cleanTxt(fileTxt(fp), tabs=tabs)

def writeFile(fp, cont:str):
    """write content to file"""
    with open(fp, 'w') as fh:
        fh.write(cont)
        fh.close()

def commonLen(arr:list):
    """find common begin length of list of iterables"""
    if not arr: return 0
    res = len(arr[0])
    for n, e2 in enumerate(arr[1:]):
        e1 = arr[n]
        ln = min(res, len(e2))
        res = 0
        for p in range(ln):
            if e1[p] == e2[p]: res += 1
            else: break
    return res

if __name__ == '__main__':
    a = [(1, 2, 4, 3), (1, 2, 4, 4), (1, 2, 4, 5)]
    print('a:', *a)
    print('common length:', commonLen(a))
