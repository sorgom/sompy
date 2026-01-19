"""find file names by extension recursion"""
from os import walk
from os.path import relpath, splitext

class FFNX:
    def __init__(self, root:str, ext:str):
        self.ext = ext
        self.root = root

    def __iter__(self):
        for dir, _, files in walk(self.root):
            dir = relpath(dir, self.root)
            if dir == '.': dir = ''
            names = (n for n, x in [splitext(f) for f in files] if x == self.ext)
            if names: yield(dir, set(names))
