import re
from collections import defaultdict

class LineNumberedFind(object):
    """Finds patterns in files and returns content found with line numbers"""
    
    def __init__(self):
        """initialize finder"""
        self.lookups = dict()
        self.results = defaultdict(dict)
        self.newline_key = '__JUST_NEWLINE__'

    def add(self, key, pattern, flags=re.NOFLAG):
        """add a pattern to look for in the files"""
        # this is the 1st clou of the search:
        # - 1st  match: the pattern itself
        # - last match: alternatively just a newline (with match key)
        self.lookups[key] = re.compile(rf'{pattern}|(?P<{self.newline_key}>\n)', flags)
        return self

    def sFile(self, fp:str):
        """search for the patterns in a file"""
        with open(fp, 'r') as fh:
            cont = fh.read()
            fh.close()
            for key, rx in self.lookups.items():
                res = []
                lnr = 1
                for mo in rx.finditer(cont):
                    # if capture was not just newline - store content found with file and line number
                    if not mo.group(self.newline_key):
                        # store file, line number, and the values found except the just newline
                        *vals, _ = mo.groups('')
                        res.append([lnr, *vals])
                    # 2nd clou:
                    # increase line counter by number of matched newlines
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
    # simple class or method pattern
    # class name, requires multiline matching
    rCla = r'^class +(\w+)'
    # method / function name, requires multiline matching
    rDef = r'^( {4})?def +(\w+)'
    # signature
    rSig = r'(.*)'
    # single line docstring
    rDoc = r'\n +"""(.*)"""'

    lnf = LineNumberedFind()
    lnf.add('CLASSES, METHODS, FUNCTIONS', rf'(?:{rCla}|{rDef}){rSig}(?:{rDoc})?', re.MULTILINE)
    
    mydir = dirname(__file__)
    files = glob(join(mydir, '*.py')) + glob(join(mydir, '*', '*.py'), recursive=True)
    lnf.sFiles(files)

    for key, cont in lnf.results.items():
        print('=' * 6, key)
        for fp, res in cont.items():
            print(f'\n{relpath(fp, mydir)}:')
            for lnr, cla, ind, met, sig, doc in res:
                fl = f'{doc}\n{ind}{" " * 7}' if doc else ''
                print(f'{ind}[{lnr:4d}] {fl}', end='')
                if cla: print('CLASS:', cla)
                else: print(f"{met}{re.sub(r':$', '', sig)}")
