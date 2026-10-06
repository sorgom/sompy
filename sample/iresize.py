"""
simple batch image resize to subfolder
usage: this script [options] folders
options:
    target images size definitions:
        -x <int> pixels width
        -y <int> pixels height
        -a <float> total number of megapixels (width x height)
    other output definitions:
        -q <20 .. 100> jpeg output quality, default 50
        -s <subfolder> output subfolder default: "_resized"
    misc
        -h this help
"""
import re
from math import sqrt
from os import makedirs
from os.path import basename, splitext, join, isfile, isdir, exists
from PIL import Image, ExifTags
from glob import iglob

#   for apple / iphone heif images
from pillow_heif import register_heif_opener
register_heif_opener()

class IResize(object):
    def __init__(self, width=None, height=None, area=None, subfolder=None, quality=None):
        self.param = None
        self.quality = 50
        try:
            if width is not None:
                self.param = int(width)
                self.sizeFunc = self.sizeFromWidth
            elif height is not None:
                self.param = int(height)
                self.sizeFunc = self.sizeFromHeight
            elif area is not None:
                self.param = 1000000 * float(area)
                self.sizeFunc = self.sizeFromArea
            else:
                raise Exception('missing size option')

            if quality is not None:
                self.quality = min(100, max(20, int(quality)))

            self.subfolder = '_resized' if subfolder is None else subfolder

        except Exception as e:
            exit(e)

        #   filter for formats that can be opened (read)
        _ = '|'.join([ex[1:] for ex, f in Image.registered_extensions().items() if f in Image.OPEN])
        self.rxImg = re.compile(rf'\.(?:{_})$', re.I)


    def process(self, folder):
        if not isdir(folder): return
        sf  = join(folder, self.subfolder)
        sfx = exists(sf)
        if sfx and not isdir(sf): return

        for f in iglob(join(folder, '*')):
            if self.rxImg.search(f) and isfile(f):
                try:
                    with Image.open(f) as img:
                        img = self.exifRotate(img)
                        width, height = self.sizeFunc(img)
                        tn, _ = splitext(basename(f))

                        trg = join(sf, f'{tn}.jpg')
                        ni = img.resize((width, height))
                        if not sfx:
                            makedirs(sf)
                            sfx = True
                        ni.save(trg, quality=self.quality)
                        print('->', width, height, basename(trg))
                except Exception as e:
                    print(f'skipped: {f} ({e})')

    def sizeFromWidth(self, img):
        return self.param, int(self.param * img.height / img.width + 0.5)
    def sizeFromHeight(self, img):
        return int(self.param * img.width / img.height + 0.5), self.param
    def sizeFromArea(self, img):
        w = img.width
        h = img.height
        r = sqrt(self.param / (w * h))
        return int(r * w + 0.5), int(r * h + 0.5)

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
        subfolder=opts.get('s'),
        quality=opts.get('q')
    )
    for arg in fglob(args):
        ir.process(arg)
