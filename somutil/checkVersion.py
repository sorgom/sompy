"""Python version check"""
from sys import version_info

def apply(major:int, minor:int, file:str):
    """apply Python version check"""
    if version_info < (major, minor):
        from os.path import basename
        from sys import exit
        raise exit(f'{basename(file)} requires Python {major}.{minor} or higher')

if __name__ == '__main__':
    print('version:', *version_info[:3])