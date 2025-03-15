"""put line breaks into mdj files for smaller git diffs"""

#   ============================================================
#   put line breaks into mdj files
#   to create smaller git diffs
#   ============================================================
#   created by Manfred Sorgo

import re
from sys import argv

def cleanMdj(*fps, lf=False):
    """put line breaks into mdj files"""
    rxOpen  = re.compile(r'([\[\{])\n?')
    rxClose = re.compile(r'\n?([\]\}],?)')
    rxLine = re.compile(r'^\s+', re.M)
    wopts = { 'newline': '\n' } if lf else {}
    for fp in fps:
        with open(fp, 'r') as fh:
            txt = fh.read()
            fh.close()
            with open(fp, 'w', **wopts) as fh:
                fh.write(rxLine.sub('', rxClose.sub(r'\n\1', rxOpen.sub(r'\1\n', txt))))
                fh.close()

if __name__ == '__main__':
    from docopts import docopts
    from fglob import fglob

    help = __doc__ + """
usage: this script [options] *.mdj
options:
-l  convert line endings to unix style
-h  this help
"""
    opts, args = docopts(help, reqArgs=True)
    lf = opts.get('l', False)
    for arg in fglob(args):
        cleanMdj(arg, lf=lf)
