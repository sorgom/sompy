"""some git utilities"""

from somproc import procOut, procOutList
from os.path import exists, join, normpath
from os import chdir, getcwd

def inRepo() -> bool:
    """check if current directory is in a git repository"""
    return procOut('git rev-parse --is-inside-work-tree') == 'true'

def repoDir() -> str:
    """top level directory of current repository"""
    return procOut('git rev-parse --show-toplevel')

def repoFiles(dir:str = ''):
    return procOutList(f'git ls-files {dir}')

def gitDiffFiles(repo:str, branch:str = None, ffunc=None) -> list:
    """existing changed or new files in repository"""
    calldir = getcwd()
    chdir(repo)
    files = []
    if not inRepo(): 
        print('not in repository')
    else:
        # output is relative to repository
        repo = repoDir()
        chdir(repo)
        def addFiles(cmd:str):
            files.extend(procOutList(cmd, codex='utf-8'))
        # diff to other branch
        if branch is not None:
            addFiles(f'git diff --name-only {branch}')
        # diff of modified files
        addFiles('git diff --name-only')
        # new files
        addFiles('git ls-files --others --exclude-standard')
        # unique
        s = set(files)
        files = [ normpath(join(repo, f)) for f in s if exists(f) and (ffunc is None or ffunc(f)) ]
    chdir(calldir)
    return files

if __name__ == '__main__':
    help = """
Show changed or new files in git repositories
Usage this script [options] [repo]
options:
-b  <branch> add diff to branch
-h  this help
"""
    from docOpts import docOpts
    from os.path import dirname

    opts, args = docOpts(help)
    branch = opts.get('b')
    args = args or [dirname(__file__)]
    for repo in args:
        print('repo:', repo)
        for fn in gitDiffFiles(repo, branch=branch):
            print(fn)
        print()
