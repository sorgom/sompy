import re
from collections import defaultdict
from pprint import pprint

class LineNumberedFind(object):
    """Finds patterns in files and returns content found with line numbers."""
    
    def __init__(self, inclBlocks:bool=False):
        """Initialize finder. Optionally let include text blocks found."""
        self.lookups = dict()
        self.results = defaultdict(list)
        self.inclBlocks = inclBlocks

    def add(self, key, pattern, flags=re.NOFLAG):
        """Add a pattern to look for in the files."""
        self.lookups[key] = re.compile(r'(' + pattern + r')|(\n)', flags)
        return self

    def sFile(self, fp:str):
        """Search for the patterns in a file."""
        with open(fp, 'r') as fh:
            cont = fh.read()
            fh.close()
            for key, rx in self.lookups.items():
                lnr = 1
                for snip, *res, br in rx.findall(cont):
                    if snip:
                        self.results[key].append([fp, lnr, snip, *res] if self.inclBlocks else [fp, lnr, *res])
                        lnr += snip.count('\n')
                    elif br:
                        lnr += 1

    def sFiles(self, fps:list[str]):
        """Search for the patterns in a list of files."""
        for fp in fps:
            self.sFile(fp)

if __name__ == '__main__':
    from os.path import dirname, join
    from glob import glob
    lnf = LineNumberedFind(inclBlocks=False)
    lnf.add('classes and methods', r'^(?:class +(\w+)|    def +(\w+))([^\n]*)(?:\n +"""(.*?)""")?', re.M | re.S)
    lnf.sFiles(glob(join(dirname(__file__), '*.py'), recursive=True))

    for key, res in lnf.results.items():
        print('#### ', key)
        fnp = None
        for fp, lnr, cla, met, sig, doc in res:
            if fnp != fp:
                print('##', fp)
                fnp = fp
            print(f'[{lnr:4d}]', doc)
            if cla: print(cla, end='')
            else: print(' ' * 6, met, end='')
            print(sig)
    
# rx = re.compile(r'^\d+') #, re.M)

# print("Regex:", rx, type(rx), rx.pattern, rx.flags, type(re.M), re.NOFLAG.value)
