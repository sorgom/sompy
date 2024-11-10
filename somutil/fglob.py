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
    from sys import argv
    for arg in fglob(argv[1:]):
        print(arg)
