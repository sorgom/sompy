# This file is used to add sompy/somutil to the sys.path
from sys import path as syspath
from os.path import dirname, abspath, join
sompath = abspath(join(dirname(__file__), '<RELPATH>'))
if sompath not in syspath:
    syspath.insert(0, sompath)
