"""put line breaks into mdj files for smaller git diffs"""

#   ============================================================
#   put line breaks into mdj files
#   to create smaller git diffs
#   ============================================================
#   created by Manfred Sorgo

import re
from sys import argv

def cleanMdj(*fps):
    """put line breaks into mdj files"""
    rxOpen  = re.compile(r'([\[\{}])\n?')
    rxClose = re.compile(r'\n?([\]\}])')
    for fp in fps:
        with open(fp, 'r') as fh:
            txt = fh.read()
            fh.close()
            with open(fp, 'w') as fh:
                fh.write(rxClose.sub(r'\n\1', rxOpen.sub(r'\1\n', txt)))
                fh.close()

if __name__ == '__main__':
    from docOpts import docOpts, docHelp
    help = __doc__ + """
usage: this script [options] *.mdj
options:
-h  this help
"""
    opts, args = docOpts(help)
    if not args:
        docHelp(help)
    cleanMdj(*args)

