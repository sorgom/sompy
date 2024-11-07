"""clean text formatting"""

import re
rxLin = re.compile(r'[ \t]+$', re.M)
rxEnd = re.compile(r'\s*$')

def cleanTxt(txt:str, tabs=None, lf=False) -> str:
    """expand tabs and remove trailing spaces"""
    if tabs: txt = txt.expandtabs(tabs)
    if lf: txt = txt.replace('\r\n', '\n').replace('\r', '\n')
    return rxEnd.sub('', rxLin.sub('', txt)) + '\n'

def cleanFile(fp:str, lf=False, **kw):
    """clean file content"""
    with open(fp, 'r') as fh:
        cont = fh.read()
        fh.close()
        wopts = { 'newline': '\n' } if lf else {}
        with open(fp, 'w', **wopts) as fh:
            # eol correction is done by open mode
            fh.write(cleanTxt(cont, lf=False, **kw))
            fh.close()

if __name__ == '__main__':
    from docOpts import docOpts
    from globify import globify

    help = __doc__ + """
usage: this script [options] files
options:
-t  <size> tab size (default 4)
-l  convert line endings to unix style
-h  this help
"""
    opts, args = docOpts(help, reqArgs=True)
    tabs = int(opts.get('t', 4))
    lf = opts.get('l', False)
    for arg in globify(args):
        cleanFile(arg, tabs=tabs, lf=lf)
