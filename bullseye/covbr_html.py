"""
convert covbr text reports to html

Usage: this script [options] folders / files
options:
    -g  <glob> glob pattern of the report files
        default: "todo_*.txt"
    -h  help
"""
from covbr import reduceCovbrCLI, rFile
import re
from itertools import batched
from os.path import basename, isfile

rxSplit = re.compile(rf'^\n*({rFile})\n*', re.M)

def getHtmlHeader(title:str):
    return """<!DOCTYPE html>
<html lang=en>
<head>
<title>##TITLE</title>
<meta charset="UTF-8">
<style>
* { font-style: normal; text-decoration: none;
	font-family:Consolas,Consolas,Menlo,monospace;
	margin-top: 0;margin-bottom: 0;
}
p { font-size:10pt; white-space:pre }
h3 { padding-left:1em; background-color: rgb(227, 227, 227); font-weight: normal; padding-bottom: 2px;}
span { background-color: hsl(120,100%,93%); }
span > u { color: blue; font-weight: bold; }
span.x { background-color: hsl(355,100%,91%); }
span > s { color: red; font-weight: bold; }
</style>
</head>
<body>
""".replace('##TITLE', title)

def getHtmlFooter():
    return '</body></html>'

def _padd(otag:str, n:int, tag:str):
    return tag + ' ' * (len(otag) - n)

def _replNok(mo):
    """indication: not covered"""    
    ind, otag, what, line = mo.groups('')
    n = 2
    # tag = ''
    match what:
        case 'T': tag = f'<u>T</u><s>F</s>'
        case 'F': tag = f'<s>T</s><u>F</u>'
        case 't': tag = f'<u>t</u><s>f</s>'
        case 'f': tag = f'<s>t</s><u>f</u>'
        case _:
            tag = f'<s>X</s>'
            n = 1
    return f'<span class=x>{ind}{_padd(otag, n, tag)}{line}</span>'

def _replOk(mo):
    """indication: covered"""    
    ind, what, line = mo.groups('')
    n = 2
    match what:
        case 'X': 
            tag = f'<u>&gt;</u>'
            n = 1
        case _:
            tag = f'<u>{what}</u>'
    # return f'<span>{_padd(beg, ind, tag)}{line}</span>'
    return f'<span>{ind}{_padd(what, n, tag)}{line}</span>'

def covbr2html(fp:str, cont:str):
    a = list(batched(rxSplit.split(cont)[1:], n=2))
    rx_ok = re.compile(r'^( *)(X|TF|tf)( .*)?', re.M)
    rx_nok = re.compile(r'^( *)(-->(\w+)?)( .*)?', re.M)
    res = []
    for f, c in a:
        c = rx_nok.sub(_replNok, c)
        c = rx_ok.sub(_replOk, c)
        res.append(f'<h3>{f}</h3>\n<p>\n{c}\n</p>')
    nfp = re.sub(r'\.\w+$', '', fp)
    ttl = basename(nfp)
    nfp = nfp + '.html' 
    ncont = '\n'.join([getHtmlHeader(ttl), *res, getHtmlFooter()])
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
    reduceCovbrCLI(func=covbr2html, doc=__doc__)