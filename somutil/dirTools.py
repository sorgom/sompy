from os.path import isdir, isfile
from pathlib import Path
from tempfile import TemporaryDirectory

class DirToolsException(Exception):
    def __init__(self, message:str):
        super().__init__(message)


class DirToolsNoDir(DirToolsException):
    def __init__(self, dir:str):
        super().__init__(f'not a directory: "{dir}"')

class DirToolsNoFile(DirToolsException):
    def __init__(self, file:str):
        super().__init__(f'not a file: "{file}"')

def chkDir(dir):
    if not isdir(dir):
        raise(DirToolsNoDir(dir))

def chkFile(file):
    if not isfile(file):
        raise(DirToolsNoFile(file))

def getCaseSense(dir):
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
            print('case sense', f'{str(getCaseSense(arg)):<5}:', arg)
        except Exception as e:
            print(e)
