"""check, add or correct include guards of C++ header files"""

from cleanTxt import cleanTxt
from os.path import basename, isfile, isdir, dirname
from glob import glob
import re
rxOnce = re.compile(r'(^ *#pragma +once\n)\n*', re.M)
rxHead = re.compile(r'^((?:\s|//.*\n)*)')
rxGuard = re.compile(r'^(#ifndef +(\w+_H)\n#define +\2\n)', re.M)
rxHeader = re.compile(r'\.h(?:pp)?$')

def addIncGuard(fp:str, tabs=None, preview=False, correct=False, sub=False):
    """add include guard to header file"""

    with open(fp, 'r') as fh:
        nm = basename(fp)
        if not rxHeader.search(nm): return
        if sub: nm = f'{basename(dirname(fp))}_{nm}'
        gs = re.sub(r'[^A-Z]', '_', nm.upper())
        guard = f'#ifndef {gs}\n#define {gs}\n'
        cont = cleanTxt(fh.read(), tabs=tabs)
        fh.close()
        old = cont
        add = True
        mo = rxGuard.search(cont)
        if mo:
            if mo.group(2) != gs:
                if correct:
                    cont = rxGuard.sub(guard, cont, count=1)
                    add = False
                else:
                    print(f'guard mismatch {fp}:\nshould be: {gs}\nbut is: {mo.group(2)}')
                    return
            else: return
        elif rxOnce.search(cont):
            cont = rxOnce.sub(rf'\1{guard}\n', cont, count=1)
        else:
            cont = rxHead.sub(rf'\1{guard}\n', cont, count=1)
        if add:
            cont = re.sub(r'\s+$', '', cont)
            cont += '\n#endif // _H\n'
        if old == cont: return
        if preview:
            print(cont)
        else:
            with open(fp, 'w') as fh:
                print(f'-> {fp}')
                fh.write(cont)
                fh.close()
    
def addIncGuards(args:list, **kws):
    """add include guards to header files"""
    for arg in args:
        if isfile(arg):
            addIncGuard(arg, **kws)
        elif isdir(arg):
            for fp in glob(f'{arg}/*.h') + glob(f'{arg}/**/*.h', recursive=True):
                addIncGuard(fp, **kws)

if __name__ == '__main__':
    from docOpts import docOpts, docHelp
    help = __doc__ + """
usage: this script [options] files / dirs
options:
-t  <size> tab size (default 4)
-s  use subfolder in guard
-c  correct guard if mismatch
-p  preview only
-h  this help
"""
    opts, args = docOpts(help)
    if not args:
        docHelp(help)
    addIncGuards(args, 
                 tabs=int(opts.get('t', 4)), 
                 preview=opts.get('p'), 
                 correct=opts.get('c'),
                 sub=opts.get('s')
                 )
