"""check, add or correct include guards of C++ header files"""

from cleanTxt import cleanTxt
from os.path import basename, isfile, isdir, dirname
from glob import glob
import re
rxOnce = re.compile(r'(^ *#pragma +once\n)\r?\n*', re.M)
rxHead = re.compile(r'^((?:\s|//.*\n)*)')
rxGuard = re.compile(r'^(#ifndef +(\w+_H)\r?\n#define +\2\n)', re.M)
rxHeader = re.compile(r'\.h(?:pp)?$')
rxIcap = re.compile(r'([a-z])([A-Z])')

def addIncGuard(fp:str, tabs=None, preview=False, correct=False, sub=False, icaps=False):
    """add include guard to header file"""

    with open(fp, 'r') as fh:
        nm = basename(fp)
        if not rxHeader.search(nm): return
        gs = rxIcap.sub(r'\1_\2', nm) if icaps else nm
        if sub: gs = f'{basename(dirname(fp))}_{gs}'
        gs = re.sub(r'[^A-Z0-9]', '_', gs.upper())
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
        cont = re.sub(r'\s+$', '', cont)
        if add:
            cont += '\n#endif // _H'
        cont += '\n'
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
    from docopts import docopts, dochelp
    help = __doc__ + """
usage: this script [options] files / dirs
options:
-t  <size> tab size (default 4)
-s  use subfolder in guard
-c  correct guard if mismatch
-i  insert underscore at intercaps
-p  preview only
-h  this help
"""
    opts, args = docopts(help)
    if not args:
        dochelp(help)
    addIncGuards(args,
                 tabs=int(opts.get('t', 4)),
                 preview=opts.get('p'),
                 correct=opts.get('c'),
                 sub=opts.get('s'),
                 icaps=opts.get('i')
                 )
