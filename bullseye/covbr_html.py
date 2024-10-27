"""
convert covbr text reports to html

Usage: this script [options] folders / files
options:
    -g  <glob> glob pattern of the report files
        default: "todo_*.txt"
    -i  <num> create index of sources at least <num> sources listed
    -h  help
"""
from covbr import Covbr
import re
from itertools import batched
from collections import Counter
from os.path import basename, isfile
from html import escape 

class CovbrHtml(Covbr):
    def __init__(self, doc=__doc__) -> None:
        super().__init__(doc)
        self.postFunc = self.process
        self.rxSplit = re.compile(rf'^\n*({self.rFile})\n*', re.M)
        self.rx_ok = re.compile(r'^( *)(X|TF|tf)( .*)?', re.M)
        self.rx_nok = re.compile(r'^( *)--&gt;(\w+)?( .*)?', re.M)
        self.rx_id = re.compile(r'\W')
        self.postFunc = self._2html
        self.counter = Counter()
        self.curr = None
        self.map = {}

    @staticmethod
    def _header(title:str):
        return """
<!DOCTYPE html>
<html lang=en>
<head>
<title>##TITLE</title>
<meta charset="UTF-8">
<style>
* { font-style: normal; text-decoration: none;
	font-family:Consolas,Consolas,Menlo,monospace;
	margin-top: 0;margin-bottom: 0;
    white-space:pre;
}
a { display: block; margin: 0; padding: 0; }
p { font-size:10pt; }
h3 { padding-left:1em; background-color: rgb(227, 227, 227); font-weight: normal; padding-bottom: 2px;}
span { background-color: hsl(120,100%,93%); }
span > u { color: blue; font-weight: bold; }
span.x { background-color: hsl(355,100%,91%); }
span > s { color: red; font-weight: bold; }
</style>
</head>
<body>
""".replace('##TITLE', title)
    
    @staticmethod
    def _footer():
        return '</body></html>'

    @staticmethod
    def _padd(otag:str, n:int, tag:str, ol:int=0):
        return tag + ' ' * (len(otag) + ol - n)

    def _replNok(self, mo):
        """indication: not covered"""    
        self.counter[self.curr] += 1
        ind, what, line = mo.groups('')
        n = 2
        match what:
            case 'T': tag = f'<u>T</u><s>F</s>'
            case 'F': tag = f'<s>T</s><u>F</u>'
            case 't': tag = f'<u>t</u><s>f</s>'
            case 'f': tag = f'<s>t</s><u>f</u>'
            case _:
                tag = f'<s>X</s>'
                n = 1
        return f'<span class=x>{ind}{self._padd(what, n, tag, 3)}{line}</span>'

    def _replOk(self, mo):
        """indication: covered"""    
        ind, what, line = mo.groups('')
        n = 2
        match what:
            case 'X': 
                tag = f'<u>&gt;</u>'
                n = 1
            case _:
                tag = f'<u>{what}</u>'
        return f'<span>{ind}{self._padd(what, n, tag)}{line}</span>'

    def _idstr(self, f:str):
        return self.rx_id.sub('_', f) if f else '_'
        # print(f)
        # return self.rx_id.sub('_', f)
    
    def _h3(self, f:str):
        id = ''
        f = f[:-1]
        if self.opts.get('i'):
            self.curr = f
            id = f' id="{self._idstr(self.curr)}"'
        return f'<h3{id}>{f}</h3>'

    def _ilink(self, f:str, n:int, w:int):
        return f'<a href="#{self._idstr(f)}">{str(n).rjust(w)}: {f}</a>'

    def _index(self):
        minc = int(self.opts.get('i', 0))
        if (not minc) or len(self.counter) < minc: return ''
        print('-> index')
        a = sorted(self.counter.items(), key=lambda x:(-x[1],x[0]))
        w = len(str(a[0][1]))
        return '\n'.join([self._ilink(f, n, w) for f, n in a if f])

    def _2html(self, fp:str, cont:str):
        self.counter.clear()
        a = list(batched(self.rxSplit.split(cont)[1:], n=2))
        res = []
        for f, c in a:
            c = escape(c)
            c = self.rx_nok.sub(self._replNok, c)
            c = self.rx_ok.sub(self._replOk, c)
            res.append(f'{self._h3(f)}\n<p>\n{c}\n</p>')
        nfp = re.sub(r'\.\w+$', '', fp)
        ttl = basename(nfp)
        nfp = nfp + '.html' 
        ncont = '\n'.join([self._header(ttl), self._index(), *res, self._footer()])
        cont = ''
        if isfile(nfp):
            with open(nfp, 'r') as fh:
                cont = fh.read()
                fh.close()
        if ncont != cont:
            print('->', nfp)
            with open(nfp, 'w') as fh:
                fh.write(ncont)
                fh.close()        

if __name__ == '__main__':
    CovbrHtml().processCLI()
