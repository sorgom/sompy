"""
simple getopt and help utility
- reads options from (preferably __doc__) string
- returns options dict and arguments
- exits with help if option "h" is given

Sample options in doc string:
-s  a switch option
-f  <some> a value option

Help output:
replaces "__file__" and "this script" with script name
"""
# author SOM, Manfred Sorgo

from getopt import getopt
from sys import argv
from os.path import basename
import re

def docRep(doc:str):
    """replace "__file__" and "this script" in doc string"""
    rxRep = re.compile(r'\b(?:__file__|this ?script)\b', re.I)
    sub = basename(argv[0])
    return rxRep.sub(sub, doc)

def docHelp(doc:str):
    """print doc string as help and exit"""
    print(docRep(doc))
    exit()

def docOpts(doc:str, help=True) -> tuple[dict, list]:
    """parse options from doc string and command line"""
    rxOpt = re.compile(r'^ *-([a-zA-Z])( +<.+?>)?', re.M)
    res = {}
    ostr = ''
    isVal = {}
    for mo in rxOpt.finditer(doc):
        key = mo.group(1)
        ostr += key
        if mo.group(2):
            ostr += ':'
            isVal[key] = True

    try:
        opts, args = getopt(argv[1:], ostr)
    except Exception:
        docHelp(doc)
    for o, v in opts:
        key = o[1]
        if help and key == 'h':
            docHelp(doc)
        res[key] = v if isVal.get(key) else True
    return res, args

if __name__ == '__main__':
    docHelp(__doc__)
