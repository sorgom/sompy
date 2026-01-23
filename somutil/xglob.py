"""
extended file or name globbing

glob        meaning         regex
------------------------------------
   .    ->  . literal       . masked
   *    ->  anything        .*
   §    ->  one character   .
   $    ->  $ literal       $ masked
   ^    ->  ^ literal       ^ masked

to get regex meaning of ?, ^, $ and *: use <
glob        regex
-----------------
   <§   ->  ?
   <*   ->  *
   <^   ->  ^
   <$   ->  $
"""
import re

class XGlob():
    "extended glob to regex transposer class"
    def __init__(self):
        self.__rxRestore = re.compile(r'[<]([\?\*\^\$\.])')
        self.__rxMask    = re.compile(r'(?<![<])([\.\*\?\^\$])')
        self.__repls = {'§':'.', '*':'.*'}

    def __repl(self, mo):
        return self.__repls.get(mo[1], f'\\{mo[1]}')

    def __flatten(self, *el) ->list:
        res = []
        for x in el:
            if isinstance(x, str):
                res.append(x)
            elif isinstance(x, (list, tuple, set)):
                for e in x: res.extend(self.__flatten(e))
        return res

    def glob2p(self, c):
        "convert xglob expression to re pattern"
        return self.__rxRestore.sub(r'\1',
            self.__rxMask.sub(self.__repl, c))

    def glob2re(self, *cs, anc=True):
        "create re object from xglob(s)"
        if not cs: return None
        fl = self.__flatten(cs)
        if not fl: return None
        cp = '|'.join([self.glob2p(c) for c in fl])
        cp = rf'(?:{cp})'
        return rf'^{cp}$' if anc else cp


if __name__ == '__main__':

    cs = ['(tmp_§{1,5}).§§{1,2}', '$sys[A-D]?wumpel.pyc?'],
    xg = XGlob()
    rx = re.compile(xg.glob2re(cs, '(tmp_*).*'))

    print(rx.pattern, type(rx))
    mo = rx.match('tmp_xyz.dat')
    if mo:
        for n, x in enumerate(mo.groups()):
            if x:
                print(n, x)
                break
    c = xg.glob2re(None)
    print('None', c)
