"""
simple line numbering for source sample markups

usage: this script [options] files
options:
-t  <size> tab size (default 4)
-h  this help
"""
import re

class SrcNums(object):
    """line numbering class"""

    def __init__(self, tabs:int=4):
        """initialize with tab size"""
        self.rxLin = re.compile(r'^', re.M)
        self.tabs = tabs

    def num(self, src:str) -> str:
        """number lines in source file"""
        with open(src, 'r') as fh:
            txt = fh.read()
            fh.close()
            self.width = len(repr(txt.count('\n') + 1))
            self.nr = 0
            return self.rxLin.sub(self._repl, txt).expandtabs(self.tabs)

    def _repl(self, *_):
        self.nr += 1
        return f'{repr(self.nr).rjust(self.width)}\t'

if __name__ == '__main__':
    from docopts import docopts
    opts, args = docopts(__doc__, reqArgs=True)
    srcNums = SrcNums(tabs=int(opts.get('t', 4)))
    print([srcNums.num(src) for src in args], sep='\n')
