
"""find documented classes, methods, functions in python files using LineNumberedFind"""

def dox():
    """do the search"""
    import sompy
    from lineNumberedFind import LineNumberedFind
    from os.path import dirname
    from os import chdir
    from glob import glob
    import re    
    
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
    
    lnf = LineNumberedFind(tabs=4)
    lnf.add('DOC', rDoc).add('CMF', rCmf, re.M).add('MOD', rMod, re.M)

    chdir(dirname(__file__))
    chdir('..')
    lnf.sFiles(glob('*/*.py'))

    fdocs = { fp: res[0][1] for fp, res in lnf['DOC'].items() }

    print('\n====== classes, methods, functions')
    pre = ' ' * 7
    for fp, res in lnf['CMF'].items():
        if fp in fdocs:
            print(f'\n{fp}')
            print('>', fdocs[fp])
            for lnr, ind, tp, nm, par, dox in res:
                print(f'[{lnr:4d}]{ind} {tp} {nm}{re.sub(r" *:$", "", par)}')
                print(f'{pre}{ind}{dox}')

    print('\n====== imported modules')
    for fp, res in lnf['MOD'].items():
        if fp in fdocs:
            print(f'\n{fp}')
            for lnr, imp, frm, what in res:
                print(f'[{lnr:4d}] ', end='')
                if imp: print(imp)
                else: print(f'{frm}: {what}')
if __name__ == '__main__':
    dox()

