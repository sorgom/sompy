
"""
find documented classes, methods, functions in python files using LineNumberedFind

Usage: this script [options] [dir]
options:
-t  <num> expand tabs to num spaces (default 4)
-i  also show imported modules
-h  this help
"""

import sompy
from lineNumberedFind import LineNumberedFind
from os import chdir, getcwd
from glob import glob
import re    

def dox(dir:str, tabs:None, imp=False):
    """do the search"""
    
    # docstring pattern (take first text line only)
    rDox = r'"""\s*(.+?)(?:\n.*?)*?"""'
    
    # search file docstrings (1st line)
    rDoc = rf'^(?:(?: *#.*)?\n)*\s*{rDox}'

    # search classes, methods, functions with docstrings
    rCmf = rf'( *)(class|def) +(\w+)(.+?)\n\s+{rDox}'
    
    # search imported modules
    rImp = r'import (.*)'
    rFrm = r'from (.+?) +import (.*)'
    rMod = rf'^ *(?:{rImp}|{rFrm})'
    
    lnf = LineNumberedFind(tabs=tabs)
    lnf.add('DOC', rDoc).add('CMF', rCmf, re.M)
    if imp: lnf.add('MOD', rMod, re.M)

    chdir(dir)
    print('directory:', getcwd())
    lnf.sFiles(glob('*.py') + glob('**/*.py', recursive=True))

    # files with file docstring
    fdocs = { fp: res[0][1] for fp, res in lnf['DOC'].items() }

    print('\n====== documented classes, methods, functions')
    pre = ' ' * 7
    for fp, res in lnf['CMF'].items():
        if fp in fdocs:
            print(f'\n{fp}')
            print('>', fdocs[fp])
            for lnr, ind, tp, nm, par, dox in res:
                print(f'[{lnr:4d}]{ind} {tp} {nm}{re.sub(r" *:$", "", par)}')
                print(f'{pre}{ind}> {dox}')

    if imp:
        print('\n====== imported modules')
        for fp, res in lnf['MOD'].items():
            if fp in fdocs:
                print(f'\n{fp}')
                for lnr, imp, frm, what in res:
                    print(f'[{lnr:4d}] ', end='')
                    if imp: print(imp)
                    else: print(f'{frm}: {what}')

if __name__ == '__main__':
    from docOpts import docOpts
    opts, args = docOpts(__doc__)
    if args: dir = args[0]
    else:
        from os.path import dirname, abspath, join
        dir = abspath(join(dirname(__file__), '..'))
    dox(dir, tabs=int(opts.get('t', 4)), imp=opts.get('i'))
