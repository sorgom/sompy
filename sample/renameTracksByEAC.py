"""
rename "00 Track00.wav" style tracks using EAC info text

usage: this script [options] <wav folder> [mp3 folder]
options
    -p  preview only
    -h  this help

"""
from os import rename
from os.path import join
import re

import sompy
from ff import FF_Base, FF_Re

class renameByEAC():
    "the re-namer class"

    def __init__(self, preview=None):
        self.rxTxt = re.compile(r'^(\d\d)\. *(.*?)[ \t]*\[(?:\d{1,2}[:.]?)+\]$', re.M)
        self.rxTrack = re.compile(r'^(\d\d) Track\1(\.\w+)$')
        self.preview = preview
        rxClean = re.compile(r' *[\\/:*?><|] *')
        self.clean = lambda c: rxClean.sub(' ', c)

    def txt2hash(self, tf:str):
        with open(tf, 'r', encoding='utf-16') as fh:
            txt = fh.read()
            return {nr:self.clean(name) for nr, name in self.rxTxt.findall(txt)}

    def transfer(self, rootWav:str, rootMp3:str=None):
        try:
            ffWav = FF_Re(rootWav, self.rxTrack)
            ffInf = FF_Base(rootWav)
            ffInf.addCheckTF(lambda e : e.name() == 'info.txt')
            ffMp3 = FF_Re(rootMp3, self.rxTrack) if rootMp3 else None
        except Exception as e:
            print(e)
            return

        dirTrackNames = {}

        ffInf.update()
        for de in ffInf:
            te = de.data[0]
            dirTrackNames[de.relpath()] = self.txt2hash(te.path())

        def goTrough(ff:FF_Re):
            ff.addCheckTD(lambda de: de.relpath() in dirTrackNames.keys())
            ff.update()
            for de in ff:
                trackNames = dirTrackNames.get(de.relpath())
                if trackNames:
                    for fe in de.data:
                        mo = self.rxTrack.match(fe.name())
                        if mo:
                            nr, ext = mo[1], mo[2]
                            nn = trackNames.get(nr)
                            if nn:
                                newPath = join(de.path(), f'{nr} {nn}{ext}')
                                if self.preview:
                                    print('old:', fe.path())
                                    print('new:', newPath)
                                    print()
                                else:
                                    rename(fe.path(), newPath)

        goTrough(ffWav)
        if ffMp3: goTrough(ffMp3)

if __name__ == '__main__':
    from docopts import docopts

    opts, args = docopts(__doc__, reqArgs=True, all=True)

    rbe = renameByEAC(preview=opts['p'])

    if len(args) > 0:
        rbe.transfer(*args[0:2])
