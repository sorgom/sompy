from os.path import isdir
from pathlib import Path
from tempfile import TemporaryDirectory

class NoDir(Exception):
    def __init__(self, dir:str):
        super().__init__(f'not a directory: "{dir}"')

def chkDir(dir):
    if not isdir(dir):
        raise(NoDir(dir))

def isCaseSensitive(dir):
    with TemporaryDirectory(dir=dir) as td:
        tp = Path(td)
        (tp / 'x').touch()
        (tp / 'X').touch()
        return len(tuple(tp.iterdir())) > 1

if __name__ == '__main__':
    from sys import argv
    for arg in argv[1:]:
        try:
            chkDir(arg)
            print('isCaseSensitive', isCaseSensitive(arg), arg)
        except Exception as e:
            print(e)
