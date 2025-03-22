"""
put line breaks behind svg file tags for smaller git diffs
also remove "UNREGISTERED" text elements
"""

import re
rxClean = re.compile(r'<text.*?>UNREGISTERED</text>')
rxTags  = re.compile(r'(<[^>]*>)\n?')
rxEnd   = re.compile(r'[ \t]+$', re.M)
rxLine  = re.compile(r'^\s+', re.M)

def cleanSvg(fp:str, lf=False, echo=False):
    """put line breaks behind svg file tags"""
    with open(fp, 'r') as fh:
        try:
            cont = fh.read()
        except Exception:
            fh.close()
            return
        fh.close()
        wopts = { 'newline': '\n' } if lf else {}
        with open(fp, 'w', **wopts) as fh:
            fh.write(rxLine.sub('', rxEnd.sub('', rxTags.sub(r'\1\n', rxClean.sub('', cont)))))
            fh.close()
            if echo: print(fp)

if __name__ == '__main__':
    from docopts import docopts
    from fglob import fglob
    help = __doc__ + """
usage: this script [options] *.svg
options:
-l  convert line endings to unix style
-e  echo processed files
-h  this help
"""
    opts, args = docopts(help)
    lf = opts.get('l', False)
    echo = opts.get('e', False)
    for arg in fglob(args):
        cleanSvg(arg, lf=lf, echo=echo)
