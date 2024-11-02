"""
cleans covbr reports from fully covered files and creates html reports

Usage: this script [options] files
options:
    -w  re-write cleaned covbr text files 
    -h  help
"""

import re
from glob import glob
from os import chdir, getcwd
from os.path import isfile, isdir, dirname, basename
from html import escape 

class Covbr2html(object):
    """covbr cleaner and html converter"""
    def __init__(self, wb:bool=False) -> None:
        self.wb = wb
        template = dirname(__file__) + '/covbr_template.html'
        with open(template, 'r') as fh:
            self.template = fh.read()
            fh.close()
        self.rFile = r'(?:\w+:/?)?\w+(?:/\w+)*\.(?:cpp|h(?:pp)?):'
        self.rEclip = r'(?: +\.\.\.\n)?'
        self.rxFile = re.compile(rf'^{self.rFile}', re.M)
        self.rxDouble = re.compile(rf'^{self.rEclip}(?:{self.rFile}\n)*({self.rFile})', re.M)
        self.rxTail = re.compile(rf'{self.rEclip}(?:{self.rFile})?\s*$')
        self.rxSpc = re.compile(rf'\s+(\n{self.rFile})')
        self.rx_fp = re.compile(rf'^\n*({self.rFile})\n*', re.M)
        self.rx_ok = re.compile(r'^( *)(X|TF|tf)($| )', re.M)
        self.rx_nok = re.compile(r'^( *)--&gt;(\w+)?( .*)?', re.M)
        self.cnt = 0
    
        print(self.rxFile.pattern)

    def write(self, fp:str, oldc:str, newc:str):
        if newc != oldc:
            with open(fp, 'w') as fh:
                fh.write(newc)
                fh.close()
                self.cnt += 1
    
    @staticmethod
    def _padd(was:str, tag:str, tl:int):
        return tag + ' ' * (len(was) - tl)

    #   indication: not covered
    def _replNok(self, mo):
        ind, what, line = mo.groups('')
        tl = 2
        match what:
            case 'T': tag = f'<u>T</u><s>F</s>'
            case 'F': tag = f'<s>T</s><u>F</u>'
            case 't': tag = f'<u>t</u><s>f</s>'
            case 'f': tag = f'<s>t</s><u>f</u>'
            case _:
                tag = ''
                tl = 0
        return f'<span>{ind}{self._padd(f'-->{what}', tag, tl)}{line}</span>'

    #   indication: covered
    def _replOk(self, mo):
        ind, what, line = mo.groups('')
        tl = 2
        match what:
            case 'X': 
                tag = ''
                tl = 0
            case _:
                tag = f'<u>{what}</u>'
        return f'{ind}{self._padd(what, tag, tl)}{line}'

    def process(self, fp:str):
        """cleans the txt file writes the html file"""
        with open(fp, 'r') as fh:
            oldc = fh.read()
            fh.close()
            if not self.rxFile.search(oldc): 
                print(f'no file names in {fp}')
                return
            # clean txt
            newc = re.sub(r'\s+$', '', 
                self.rxTail.sub('', 
                    self.rxSpc.sub(r'\n\1', 
                        self.rxDouble.sub(r'\n\1', oldc.replace('\r', ''))))) + '\n'
            if self.wb:
                self.write(fp, oldc, newc)
            
            newc = self.rx_ok.sub(self._replOk, 
                    self.rx_nok.sub(self._replNok,
                        self.rx_fp.sub(r'\n<em>\1</em>\n', escape(newc)))).strip()
            nfp = re.sub(r'\.\w+$', '', fp)
            ttl = basename(nfp)
            nfp = nfp + '.html'
            newc = self.template.replace('##TITLE', ttl, 1).replace('##CONTENT', newc, 1)
            oldc = ''
            if isfile(nfp):
                with open(nfp, 'r') as fh:
                    oldc = fh.read()
                    fh.close()
            self.write(nfp, oldc, newc)

if __name__ == '__main__':
    import sompy
    from docOpts import docOpts
    from globify import globify

    opts, args = docOpts(__doc__, reqArgs=True)
    cb = Covbr2html(opts.get('w', False))
    for arg in globify(args):
        cb.process(arg)
    if cb.cnt: print('>', cb.cnt)
