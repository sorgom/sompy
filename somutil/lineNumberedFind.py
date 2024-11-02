
"""
Find patterns in files, return content found with line numbers

see also sample: sample/dox.py
"""

# due to re.NOFLAG
import checkVersion
checkVersion.apply(3, 12, __file__)

import re

class LineNumberedFind(dict):
    """Finds patterns in files and returns content found with line numbers"""

    def __init__(self, tabs=None, clean=True):
        """initialize finder"""
        self.lookups = dict()
        self.newline_key = '__JUST_NEWLINE__'
        self.rxLe = re.compile(r'[ \t]+$', re.M)
        self.tabs = tabs
        self.clean = clean

    def add(self, key, pattern, flags=re.NOFLAG):
        """add a pattern to look for in the files"""
        # line numbering (1):
        # - 1st  match: the pattern itself
        # - last match: alternatively just a newline (with match key)
        self.lookups[key] = re.compile(rf'{pattern}|(?P<{self.newline_key}>\n)', flags)
        self[key] = dict()
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
                        res.append((lnr, *vals))
                        # line numbering (3):
                        # add number of newlines of the whole match to the line count
                        lnr += mo[0].count('\n')
                if res:
                    self[key][fp] = res

    def sFiles(self, fps:list[str]):
        """search for the patterns in a list of files"""
        for fp in fps:
            self.sFile(fp)

if __name__ == '__main__':
    print(__doc__)

