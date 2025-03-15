"""
put line breaks behind svg file tags for smaller git diffs
also remove "UNREGISTERED" text elements
"""

from somtxt import fileTxt, writeFile
import re
from sys import argv

def cleanSvg(*fps, lf=False):
    """put line breaks behind svg file tags"""
    rxClean = re.compile(r'<text.*?>UNREGISTERED</text>')
    rxTags  = re.compile(r'(<[^>]*>)\n?')
    rxEnd   = re.compile(r'[ \t]+$', re.M)
    rxLine  = re.compile(r'^\s+', re.M)
    wopts = { 'newline': '\n' } if lf else {}
    for fp in fps:
        with open(fp, 'r') as fh:
            txt = fh.read()
            fh.close()
            with open(fp, 'w', **wopts) as fh:
                fh.write(rxLine.sub('', rxEnd.sub('', rxTags.sub(r'\1\n', rxClean.sub('', txt)))))
                fh.close()

if __name__ == '__main__':
    from docopts import docopts
    from fglob import fglob
    help = __doc__ + """
usage: this script [options] *.svg
options:
-l  convert line endings to unix style
-h  this help
"""
    opts, args = docopts(help, reqArgs=True)
    lf = opts.get('l', False)
    for arg in fglob(args):
        cleanSvg(arg, lf=lf)
