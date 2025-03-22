"""file globbing for windows CLI"""

from glob import glob
from os import name as os_name

def fglob(args):
    """file globbing for windows CLI"""
    if (os_name == 'posix'):
        for arg in args: yield arg
    else:
        for arg in args:
            for gl in glob(arg): yield gl

if __name__ == '__main__':
    from docopts import docopts
    help = __doc__ + """
usage:
- call this script [options] args > temporary.cmd
- check %errorlevel%
- call temporary.cmd
options:
-c  <cmd> call command with placeholder <ARG> for each globbed arg
-p  <placeholder> set placeholder for -c option
    default: <ARG>
-v  <varname> set variable name for globbed args
    default: _args
-h  this help
"""
    opts, args = docopts(help)
    args = fglob(args)
    cmd = opts.get('c')
    if cmd:
        ph = opts.get('p', '<ARG>')
        for arg in args:
            print(cmd.replace(ph, arg))
    else:
        print(f"set {opts.get('v', '_args')}=", end='')
        print(*list(fglob(args)))
