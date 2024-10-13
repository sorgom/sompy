"""clean text formatting"""

import re
rxLin = re.compile(r'[ \t]+$', re.M)
rxEnd = re.compile(r'\s*$')

def cleanTxt(txt:str, tabs=None) -> str:
    """expand tabs and remove trailing spaces"""
    if tabs: txt = txt.expandtabs(tabs)
    return rxEnd.sub('', rxLin.sub('', txt)) + '\n'

def cleanFile(fp:str, tabs=None):
    """clean file content"""
    with open(fp, 'r') as fh:
        cont = fh.read()
        fh.close()
        with open(fp, 'w') as fh:
            fh.write(cleanTxt(cont, tabs=tabs))
            fh.close()

if __name__ == '__main__':
    from docOpts import docOpts, docHelp
    help = __doc__ + """
usage: this script [options] files
options:
-t  <size> tab size (default 4)
-h  this help
"""
    opts, args = docOpts(help)
    if not args:
        docHelp(help)
    for fp in args:
        cleanFile(fp, tabs=int(opts.get('t', 4)))
                  