"""
simple batch image resizer
source.img -> source_123x456.jpg if same folder
source.img -> source.jpg if different folder
usage: this script [options] image files or folders
options:
    target images size definitions:
        -x <int> pixels width
        -y <int> pixels height
        -a <float> total number of megapixels (width x height)
    other output definitions:
        -q <20 .. 100> jpeg output quality, default 50
        -o <folder> output folder (if different than source folder)
    misc
        -h this help
"""
import re
from math import sqrt
from os import makedirs
from os.path import dirname, basename, abspath, normpath, splitext, join, isabs
from PIL import Image, ExifTags
#   for apple / iphone heif images
from pillow_heif import register_heif_opener

class IResize(object):
    def __init__(self, width=None, height=None, area=None, folder=None, quality=None):
        self.param = None
        self.folder = None
        self.quality = 50
        try:
            if width is not None:
                self.param = int(width)
                self.sizeFunc = self.sizeFromWidth
                what = 'width'
            elif height is not None:
                self.param = int(height)
                self.sizeFunc = self.sizeFromHeight
                what = 'height'
            elif area is not None:
                self.param = 1000000 * float(area)
                self.sizeFunc = self.sizeFromArea
                what = 'area'
            else:
                exit()

            if quality is not None:
                self.quality = min(100, max(20, int(quality)))

            if folder is not None:
                self.folder = normpath(folder)
                if isabs(self.folder):
                    makedirs(self.folder, exist_ok=True)
                    self.trgNameFunc = self.trgNameAbs
                else:
                    self.trgNameFunc = self.trgNameSub

        except Exception as e:
            exit()

        print(what, self.param)

        self.rxDone = re.compile(r'^.*_\d+x\d+\.\w{1-4}$', re.I)

    def process(self, srcs):
        for src in srcs:
            if self.rxDone.match(src):
                continue
            try:
                with Image.open(src) as img:
                    img = self.exifRotate(img)
                    width, height = self.sizeFunc(img)
                    trg = self.trgNameFunc(src, width, height)
                    ni = img.resize((width, height))
                    ni.save(trg, quality=self.quality)
                    print('->', width, height, trg)
            except Exception as e:
                print(f'skipped: {src} ({e})')

    def sizeFromWidth(self, img):
        return self.param, int(self.param * img.height / img.width + 0.5)
    def sizeFromHeight(self, img):
        return int(self.param * img.width / img.height + 0.5), self.param
    def sizeFromArea(self, img):
        w = img.width
        h = img.height
        r = sqrt(self.param / (w * h))
        return int(r * w + 0.5), int(r * h + 0.5)

    def trgNameSub(self, src, width, height):
        bnm, _ = splitext(basename(src))
        dir = join(abspath(dirname(src)), self.folder)
        makedirs(dir, exist_ok=True)
        return join(dir, f'{bnm}.jpg')

    def trgNameAbs(self, src, width, height):
        dir = normpath(abspath(dirname(src)))
        bnm, _ = splitext(basename(src))
        if self.folder is None or self.folder == dir:
            bnm = f'{bnm}_{width}x{height}'
        else: dir = self.folder
        return join(dir, f'{bnm}.jpg')

    @staticmethod
    def exifRotate(img):
        try:
            exif = img._getexif()
            if exif:
                orientation_key = next(k for k, v in ExifTags.TAGS.items() if v == 'Orientation')
                orientation = exif.get(orientation_key, None)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except Exception as e:
            print(f"EXIF rotation skipped: {e}")
        return img

import sompy

if __name__ == '__main__':
    from docopts import docopts
    from fglob import fglob
    opts, args = docopts(__doc__, reqArgs=True)
    ir = IResize(
        width=opts.get('x'),
        height=opts.get('y'),
        area=opts.get('a'),
        folder=opts.get('o'),
        quality=opts.get('q')
    )
    ir.process(fglob(args))
