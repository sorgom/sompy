from EnumExif import Exif
from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
register_heif_opener()

import re
rxModel = re.compile(r'^(\w+).*')
# 1 year
# 2 month
# 3 day
# 4 hour
# 5 min
# 5 sec
# DateTime: 2008:04:20 18:28:01
# Photoshop XMLPacket <exif:DateTimeOriginal>
# 2008-04-20T16:12:48+01:00
rDate = r'(\d{4}).(\d{2}).(\d{2}).(\d{2}).(\d{2}).(\d{2})'
rxDateTime = re.compile(r'^' + rDate)
rxDateTimeOriginal = re.compile(r'^.*<exif:DateTimeOriginal>' + rDate + r'.*', re.S | re.I)
rSub = r'\1-\2-\3_\4\5\6'

# tag listing for md file
# for tag, id in sorted(TAGS.items(), key=lambda i: i[1].upper()):
#     print('|', id, '|', tag, '|')
# exit>()

from glob import glob
from os.path import join, dirname, splitext

imgDir = join(dirname(__file__), '..', 'tmp_img')

imgExt = tuple(('.jpg', '.jpeg', '.png', '.tif', '.tiff',  '.heic', '.avif'))


for file in glob(join(imgDir, '**', '*.*'), recursive=True):
    if file.lower().endswith(imgExt):
        try:
            image = Image.open(file)
            xdata = image.getexif()
            print('file', file)
            #   photoshop TIF
            xm = xdata.get(Exif.XMLPacket.value)
            sw = xdata.get(Exif.Software.value)
            if sw and xm and 'adobe' in sw.lower() and rxDateTimeOriginal.match(str(xm)):
                ds = rxDateTimeOriginal.sub(rSub, str(xm))
            else:
                date = xdata.get(Exif.DateTime.value)
                if date is None: continue
                ds = rxDateTime.sub(rSub, date)
            model = rxModel.sub(r'\1', xdata.get(Exif.Model.value, 'nn'))
            newName = f'{ds}_{model.lower()}{splitext(file)[1]}'
            target = join(imgDir, newName)
            print('target', target)

            # for tag_id in xdata:
            #     tag = TAGS.get(tag_id, tag_id)
            #     data = xdata.get(tag_id)
            #     # decode bytes
            #     if isinstance(data, bytes):
            #         data = data.decode()
            #     print(f'{tag_id:<16}: {tag:<25}: {data}')
            # model = rxModel.sub(r'\1', xdata.get(Exif.Model.value, 'nn'))
            # date = xdata.get(Exif.DateTime.value)
            # if date is None: continue
            # newName = date.replace(':', '-', 2).replace(':', '').replace(' ', '_') + '_' + model.lower() + splitext(file)[1]
            # target = join(imgDir, newName)
            # print('target', target)

        except Exception as e:
            print(e)
            pass

    # all tags

#   result
