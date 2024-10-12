"""sub process utilities"""
#   ============================================================
#   some commonly used features
#   ============================================================
#   created by Manfred Sorgo

import re
from os.path import basename, exists
from subprocess import Popen, DEVNULL, PIPE
from os import name as oname
from sys import exit

rxEnd = re.compile(r'\s*$')

#   so we just go by extension
def procOut(call, codex='ascii') -> str:
    """run process and return stdout"""
    with Popen(call, stdout=PIPE, shell=True) as proc:
        return rxEnd.sub('', proc.stdout.read().decode(codex))

def procOutList(call, codex='ascii'):
    """run process and return stdout as list"""
    return procOut(call, codex).split('\n')

def repoDir():
    return procOut('git rev-parse --show-toplevel')

def repoFiles(dir:str = ''):
    return procOutList(f'git ls-files {dir}')

def mdCode(cont:str):
    return '\n'.join(['```', cont, '```'])

def checkLinux():
    if oname != 'posix':
        print('linux required')
        exit(-1)

if __name__ == '__main__':
    pass
