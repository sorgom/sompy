"""
creates som.py which extends system path to include the somutil directory

Call this script from target folder.
usage: this script [options]
options:
-h  this help
-c  create som.py
-n  <name> create <name>.py instead
-f  force creation if file exists
-p  preview file content
"""

if __name__ == '__main__':
    from docOpts import docOpts, docHelp
    from os import getcwd
    from os.path import dirname, relpath, join, exists
    import re
    opts, args = docOpts(__doc__)
    
    if not (opts.get('c') or opts.get('p')):
        docHelp(__doc__)

    cwdPath = getcwd()
    myPath = dirname(__file__)

    relPath = relpath(myPath, cwdPath).replace('\\', '/')

    if relPath == '.': docHelp(__doc__)

    name = re.sub(r'\.py$', '', opts.get('n', 'som')) + '.py'
    target = join(cwdPath, name)

    print('target :', target)
    print('relPath:', relPath)

    if exists(target) and not opts.get('f'):
        print(f'file {name} exists')
        exit()

    template = join(myPath, '..', 'templates', 'som.py')
    with open(template, 'r') as fh:
        cont = fh.read()
        fh.close()
    cont = cont.replace('<RELPATH>', relPath)

    if opts.get('p'):
        print(cont)
    else:
        with open(target, 'w') as fh:
            fh.write(cont)
            fh.close()
