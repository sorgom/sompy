import sompy
from ffnx import FFNX

# class FFNX:
#     def __init__(self, root:str, ext:str):
#         self.ext = ext
#         self.root = root

#     def __iter__(self):
#         for dir, _, files in walk(self.root):
#             dir = relpath(dir, self.root)
#             if dir == '.': dir = ''
#             names = (n for n, x in [splitext(f) for f in files] if x == self.ext)
#             if names: yield(dir, set(names))

if __name__ == '__main__':
    from os import chdir, getcwd
    from os.path import dirname, abspath, basename, join, getmtime



    sRoot = 'M:/EAC'
    # dRoot = 'C:/TEMP/Music'
    dRoot = 'M:/Musik'

    def work(dir:str, mk:bool, wav:set, mp3:set={}):
        sDir = join(sRoot, dir)
        dDir = join(dRoot, dir)
        if mk: print('mkdirs(dDir)')
        for name in wav:
            sf = join(sDir, f'{name}.wav')
            df = join(dDir, f'{name}.mp3')
            if (not name in mp3) or (getmtime(sf) > getmtime(df)):
                print('trans:', dir, name)


    lSrc = list(FFNX(sRoot, '.wav'))
    lDst = list(FFNX(dRoot, '.mp3'))
    hSrc = { dir:names for dir, names in lSrc }
    hDst = { dir:names for dir, names in lDst }


    for dir, dns in lDst:
        sns = hSrc.get(dir)
        if sns:
            dels = dns - sns
            if dels: print('delete:', dir, ':', *dels)

    for dir, sns in lSrc:
        dns = hDst.get(dir)
        if dns:
            work(dir, False, sns, dns)
        else:
            work(dir, True, sns)
