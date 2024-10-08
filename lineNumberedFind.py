import re
from sys import version_info

if version_info < (3, 12):
    from os.path import basename
    raise Exception(f'{basename(__file__)} requires Python 3.12 or higher')

class LineNumberedFind(object):
    
    """Finds patterns in files and returns content found with line numbers"""
    
    def __init__(self, tabs=None, clean=True):
        """initialize finder"""
        self.lookups = dict()
        self.results = dict()
        self.newline_key = '__JUST_NEWLINE__'
        self.rxLe = re.compile(r' +$', re.M)
        self.tabs = tabs
        self.clean = clean

    def add(self, key, pattern, flags=re.NOFLAG):
        """add a pattern to look for in the files"""
        # line numbering (1):
        # - 1st  match: the pattern itself
        # - last match: alternatively just a newline (with match key)
        self.lookups[key] = re.compile(rf'{pattern}|(?P<{self.newline_key}>\n)', flags)
        self.results[key] = dict()
        return self

    def sFile(self, fp:str):
        """search for the patterns in a file"""
        with open(fp, 'r') as fh:
            # read file content, expand tabs, remove trailing spaces
            cont = fh.read()
            fh.close()
            if self.tabs: cont = cont.expandtabs(self.tabs)
            if self.clean: cont = self.rxLe.sub('', cont)

            for key, rx in self.lookups.items():
                res = []
                lnr = 1
                for mo in rx.finditer(cont):
                    # line numbering (2):
                    # if match was just newline - increase line count
                    if mo.group(self.newline_key):
                        lnr += 1
                    # if match was not just newline - store content found with line count
                    else:
                        # store line number and values found (except the just newline)
                        *vals, _ = mo.groups('')
                        res.append([lnr, *vals])
                        # line numbering (3):
                        # add number of newlines in the match to the line count
                        lnr += mo[0].count('\n')
                if res:
                    self.results[key][fp] = res

    def sFiles(self, fps:list[str]):
        """search for the patterns in a list of files"""
        for fp in fps:
            self.sFile(fp)

if __name__ == '__main__':
    # SAMPLE
    # search for classes methods and functions in all .py files this directory and below

    from os.path import dirname, join, relpath
    from glob import glob
    
    # search classes, methods, functions, single line docstrings
    rCmf = r'^( *)(class|def) +(\w+)(.*)(?:\n\s+"""(.*)""")?'
    
    # search imported modules
    rImp = r'import (.*)'
    rFrm = r'from (.+?) +import (.*)'
    rMod = rf'^ *(?:{rImp}|{rFrm})'
    
    lnf = LineNumberedFind(tabs=4).add('CMF', rCmf, re.M).add('MOD', rMod, re.M)

    mydir = dirname(__file__)
    files = glob(join(mydir, '*.py')) + glob(join(mydir, '**', '*.py'), recursive=True)
    lnf.sFiles(files)

    def pOut(fp):
        print(f'\n{relpath(fp, mydir).replace('\\', '/')}:')

    print('====== classes, methods, functions')
    pre = ' ' * 6
    for fp, res in lnf.results['CMF'].items():
        pOut(fp)
        for lnr, ind, tp, nm, par, doc in res:
            sig = re.sub(r':$', '', f'{tp} {nm}{par}')
            print(f'[{lnr:4d}]{ind} ', end='')
            if doc:
                print('>', doc)
                print(f'{pre} {ind}{sig}')
            else:
                print(sig)
    print()
    print('====== imported modules')
    for fp, res in lnf.results['MOD'].items():
        pOut(fp)
        for lnr, imp, frm, what in res:
            print(f'[{lnr:4d}] ', end='')
            if imp: print(imp)
            else: print(f'{frm}: {what}')
