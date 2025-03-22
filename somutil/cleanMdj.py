"""put line breaks into mdj files for smaller git diffs"""

import re
from sys import argv
rxOpen  = re.compile(r'([\[\{])\n?')
rxClose = re.compile(r'\n?([\]\}],?)')
rxLine = re.compile(r'^\s+', re.M)

def cleanMdj(fp:str, lf=False, echo=False):
    """put line breaks into mdj files"""
    with open(fp, 'r') as fh:
        try:
            cont = fh.read()
        except Exception:
            fh.close()
            return
        fh.close()
        wopts = { 'newline': '\n' } if lf else {}
        with open(fp, 'w', **wopts) as fh:
            fh.write(rxLine.sub('', rxClose.sub(r'\n\1', rxOpen.sub(r'\1\n', cont))))
            fh.close()
            if echo: print(fp)

if __name__ == '__main__':
    from docopts import docopts
    from fglob import fglob

    help = __doc__ + """
usage: this script [options] *.mdj
options:
-l  convert line endings to unix style
-e  echo processed files
-h  this help
"""
    opts, args = docopts(help)
    lf = opts.get('l', False)
    echo = opts.get('e', False)
    for arg in fglob(args):
        cleanMdj(arg, lf=lf, echo=echo)
