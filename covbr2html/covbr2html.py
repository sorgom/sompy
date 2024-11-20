"""
create html reports from covbr text reports

usage: this script [options] files
options:
    -o  <directory> output directory
    -c  highlight covered items
    -f  show fully covered sources
    -h  help
"""

import re
from os.path import dirname, basename, join, isdir
from os import makedirs
from html import escape

class Covbr2html(object):
    """covbr to html converter"""
    def __init__(self, hc=False, odir=None, fc=False):
        self.err = False
        try:
            template = join(dirname(__file__), 'covbr_template.html')
            with open(template, 'r') as fh:
                self.template = fh.read()
                fh.close()
        except:
            print('template not found:', template)
            self.err = True
            return

        self.odir = odir
        if odir:
            if not isdir(odir):
                try:
                    makedirs(odir)
                except:
                    print('cannot create output directory:', odir)
                    self.err = True
                    return

        self.hc = hc
        self.fc = fc

        #   check if any uncovered items
        self.rxCheck = re.compile(r'^ *-->\w?( .*)?$', re.M)

        rFile = r'(?:\w+:/?)?\w+(?:/\w+)*\.(?:cpp|h(?:pp)?):'
        #   single file
        self.rxFile = re.compile(rf'^{rFile}', re.M)
        #   multiple files no catch
        self.rxFiles = re.compile(rf'^(?:{rFile}\n)*{rFile}', re.M)
        #   multiple files catch last
        self.rxLast = re.compile(rf'^(?:{rFile}\n)*({rFile})', re.M)
        #   single file with emphasis end tag
        self.rxFileEm = re.compile(rf'^{rFile}</em>', re.M)
        #   clean tailing emphasis
        self.rxTailEm = re.compile(rf'</em>\s*$')

        self.rxTail = re.compile(rf'(?:{rFile})?\s*$')
        self.rxOk = re.compile(r'^( *)(X|TF|tf)(?:$| (.*))', re.M)
        self.rxNok = re.compile(r'^( *)--&gt;(\w+)?( .*)?', re.M)
        self.okb = '<i>'  if hc else ''
        self.oke = '</i>' if hc else ''

        self.tagMap = {
            'T': '<u>T</u><s>F</s>  ',
            'F': '<s>T</s><u>F</u>  ',
            't': '<u>t</u><s>f</s>  ',
            'f': '<s>t</s><u>f</u>  '
        }

    def ok(self):
        return not self.err

    def write(self, fp:str, cont:str):
        if self.odir:
            fp = join(self.odir, basename(fp))
        with open(fp, 'w') as fh:
            fh.write(cont)
            fh.close()

    #   indication: not covered
    def _replNok(self, mo):
        ind, what, line = mo.groups('')
        tag = self.tagMap.get(what, '<s>X</s>  ')
        return f'<b>{ind}{tag}{line}</b>'

    #   indication: covered
    def _replOk(self, mo):
        ind, what, line = mo.groups('')
        tag = '  ' if what == 'X' else f'<u>{what}</u> '
        return f'{self.okb}{ind}{tag}{line}{self.oke}'

    def process(self, fp:str):
        """clean txt file write html file"""
        if self.err: return
        cont = ''
        try:
            with open(fp, 'r') as fh:
                cont = fh.read()
                fh.close()
        except: return
        if not (self.fc or self.rxCheck.search(cont)): return
        # clean txt
        if not self.fc:
            cont = re.sub(r'\s+$', '',
                self.rxTail.sub('',
                    self.rxLast.sub(r'\1', cont)))

        # create html
        cont = escape(cont)
        if self.fc:
            cont = self.rxFileEm.sub(r'<em>\g<0>', self.rxTailEm.sub('', self.rxFiles.sub(r'\g<0></em>', cont)))
            if self.hc:
                cont = self.rxFiles.sub(r'<i>\g<0></i>', cont)
        else:
            cont = self.rxFile.sub(r'<em>\g<0></em>', cont)

        cont = self.rxOk.sub(self._replOk, self.rxNok.sub(self._replNok, cont)).strip()

        fp = re.sub(r'\.\w+$', '', fp)
        ttl = basename(fp)
        cont = self.template.replace('##TITLE', ttl, 1).replace('##CONTENT', cont, 1)
        self.write(fp + '.html', cont)

if __name__ == '__main__':
    import sompy
    from docopts import docopts
    from fglob import fglob

    opts, args = docopts(__doc__, reqArgs=True)
    cb = Covbr2html(hc=opts.get('c', False), fc=opts.get('f', False), odir=opts.get('o'))
    if cb.ok():
        for arg in fglob(args):
            cb.process(arg)
