"""
put line breaks behind svg file tags for smaller git diffs
also remove "UNREGISTERED" text elements
"""

from somtxt import fileTxt, writeFile
import re
from sys import argv

def cleanSvg(*fps):
    """put line breaks behind svg file tags"""
    rxClean = re.compile(r'<text.*?>UNREGISTERED</text>')
    rxTags  = re.compile(r'(<[^>]*>)\n?')
    rxEnd   = re.compile(r'[ \t]+$', re.M)
    rxLine  = re.compile(r'^\n', re.M)
    for fp in fps:
        with open(fp, 'r') as fh:
            txt = fh.read()
            fh.close()
            with open(fp, 'w') as fh:
                fh.write(rxLine.sub('', rxEnd.sub('', rxTags.sub(r'\1\n', rxClean.sub('', txt)))))
                fh.close()

if __name__ == '__main__':
    from docOpts import docOpts, docHelp
    help = __doc__ + """
usage: this script [options] *.svg
options:
-h  this help
"""
    opts, args = docOpts(help)
    if not args:
        docHelp(help)
    cleanSvg(*argv[1:])
    

