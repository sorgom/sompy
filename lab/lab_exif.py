from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
register_heif_opener()

import re
rxModel = re.compile(r'^(\w+).*')

# tag listing for md file
# for tag, id in sorted(TAGS.items(), key=lambda i: i[1].upper()):
#     print('|', id, '|', tag, '|')
# exit>()

from glob import glob
from os.path import join, dirname, splitext

imgDir = join(dirname(__file__), '..', 'tmp_img')

for img in glob(join(imgDir, '**', '*.*'), recursive=True):
    try:
        image = Image.open(img)
        exifdata = image.getexif()
        model = rxModel.sub(r'\1', exifdata.get(272, 'nn'))
        date = exifdata.get(306)
        if date is None: continue
        newName = date.replace(':', '-', 2).replace(':', '').replace(' ', '_') + '_' + model.lower() + splitext(img)[1]
        target = join(imgDir, newName)
        print('target', target)

    except:
        pass

    # all tags
    # for tag_id in exifdata:
    #     tag = TAGS.get(tag_id, tag_id)
    #     data = exifdata.get(tag_id)
    #     # decode bytes
    #     if isinstance(data, bytes):
    #         data = data.decode()
    #     print(f"{tag_id:<16}: {tag:<25}: {data}")

#   result
