import re
from collections import defaultdict

class LineNumberedFind(object):
    """Finds patterns in files and returns content found with line numbers"""
    
    def __init__(self):
        """initialize finder"""
        self.lookups = dict()
        self.results = defaultdict(list)

    def add(self, key, pattern, flags=re.NOFLAG):
        """add a pattern to look for in the files"""
        # this is the 1st clou of the search:
        # - 1st  match: the whole pattern wrapped in a group
        # - last match: alternatively a newline
        self.lookups[key] = re.compile(r'(' + pattern + r')|(\n)', flags)
        return self

    def sFile(self, fp:str):
        """search for the patterns in a file"""
        with open(fp, 'r') as fh:
            cont = fh.read()
            fh.close()
            for key, rx in self.lookups.items():
                lnr = 1
                for all, *res, br in rx.findall(cont):
                    # this is the 2nd clou of the search:
                    # pattern or newline matched
                    # - if pattern matched: 
                    #   - store content found with file and line number
                    #   - add the content number of newlines to the line numbers' counter
                    if all:
                        self.results[key].append([fp, lnr, all, *res])
                        lnr += all.count('\n')
                    # - otherwise just increase numbers' counter
                    else: lnr += 1

    def sFiles(self, fps:list[str]):
        """search for the patterns in a list of files"""
        for fp in fps:
            self.sFile(fp)

if __name__ == '__main__':
    from os.path import dirname, join
    from glob import glob
    lnf = LineNumberedFind()
    # simple class or method pattern
    # $1: class name
    # $2: method name
    # $3: signature
    # $4: docstring
    lnf.add('CLASSES AND METHODS', r'^(?:class +(\w+)|    def +(\w+))([^\n]*)(?:\n +"""(.*?)""")?', re.M | re.S)
    
    # search for classes and methods in all .py files this directory and below
    mydir = dirname(__file__)
    files = glob(join(mydir, '*.py')) + glob(join(mydir, '*', '*.py'), recursive=True)
    lnf.sFiles(files)

    for key, res in lnf.results.items():
        print('=' * 6, key)
        currfp = None
        for fp, lnr, all, cla, met, sig, doc in res:
            if currfp != fp:
                print('FILE: ', fp)
                currfp = fp
            print(f'[{lnr:4d}] {doc}')
            if cla: print('CLASS:', cla)
            else: print(' ' * 6, f'{met}{re.sub(r':$', '', sig)}')