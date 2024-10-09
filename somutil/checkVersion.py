from sys import version_info

def apply(major:int, minor:int, file:str):
    if version_info < (major, minor):
        from os.path import basename
        from sys import exit
        raise exit(f'{basename(file)} requires Python {major}.{minor} or higher')
