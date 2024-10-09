"""
simple line numbering for source sample markups

usage: this script [options] files
options:
-t  <size> tab size (default 4)
-h  this help
"""
#   created by Manfred Sorgo

import re

class SrcNums(object):
    def __init__(self, tabs:int=4):
        self.rxLin = re.compile(r'^', re.M)
        self.tabs = tabs

    def num(self, src, num:int=0):
        with open(src, 'r') as fh:
            txt = fh.read()
            fh.close()
            nl = txt.count('\n') + 1
            ln = len(str(nl))
            self.frm = f'%0{ln}d\t'
            self.nr = 0
            txt = self.rxLin.sub(self.repl, txt).expandtabs(self.tabs)
            if num: print()
            print(txt)

    def repl(self, *_):
        self.nr += 1
        return self.frm % self.nr
    
if __name__ == '__main__':
    from docOpts import docOpts, docHelp
    opts, args = docOpts(__doc__)
    if not args:
        docHelp(__doc__)
    srcNums = SrcNums(tabs=int(opts.get('t', 4)))
    for num, src in enumerate(args):
        srcNums.num(src, num)
