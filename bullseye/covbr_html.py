"""
cleans covbr reports from fully covered files and creates html reports

Usage: this script [options] folders / files
options:
    -g  <glob> glob pattern of the report files
        default: "todo_*.txt"
    -h  help
"""
from covbr import Covbr
import re
from os.path import basename, isfile, dirname
from html import escape 

class CovbrHtml(Covbr):
    """covbr cleaner and html creator"""
    def __init__(self, doc=__doc__) -> None:
        super().__init__(doc)
        self.rx_fp = re.compile(rf'^\n*({self.rFile})\n*', re.M)
        self.rx_ok = re.compile(r'^( *)(X|TF|tf)( .*)?', re.M)
        self.rx_nok = re.compile(r'^( *)--&gt;(\w+)?( .*)?', re.M)
        template = dirname(__file__) + '/covbr_template.html'
        with open(template, 'r') as fh:
            self.template = fh.read()
            fh.close()

    @staticmethod
    def _padd(was:str, tag:str, tl:int):
        return tag + ' ' * (len(was) - tl)

    # indication: not covered
    def _replNok(self, mo):
        ind, what, line = mo.groups('')
        tl = 2
        match what:
            case 'T': tag = f'<u>T</u><s>F</s>'
            case 'F': tag = f'<s>T</s><u>F</u>'
            case 't': tag = f'<u>t</u><s>f</s>'
            case 'f': tag = f'<s>t</s><u>f</u>'
            case _:
                tag = f'<s>X</s>'
                tl = 1
        return f'<span class=x>{ind}{self._padd(f'-->{what}', tag, tl)}{line}</span>'

    # indication: covered
    def _replOk(self, mo):
        ind, what, line = mo.groups('')
        tl = 2
        match what:
            case 'X': 
                tag = f'<u>&gt;</u>'
                tl = 1
            case _:
                tag = f'<u>{what}</u>'
        return f'<span>{ind}{self._padd(what, tag, tl)}{line}</span>'

    def postFunc(self, fp:str, cont:str):
        """creates html report"""
        cont = self.rx_ok.sub(self._replOk, 
                    self.rx_nok.sub(self._replNok,
                        self.rx_fp.sub(r'\n<em>\1</em>\n', escape(cont)))).strip()
        nfp = re.sub(r'\.\w+$', '', fp)
        nfp = nfp + '.html'
        newc = self.template.replace('##TITLE', basename(nfp), 1).replace('##CONTENT', cont, 1)
        oldc = ''
        if isfile(nfp):
            with open(nfp, 'r') as fh:
                oldc = fh.read()
                fh.close()
        self.write(nfp, oldc, newc)

if __name__ == '__main__':
    CovbrHtml().processCLI()
