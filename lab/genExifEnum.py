"""generate enumeration for PIL exif tags"""
from collections import defaultdict
from PIL.ExifTags import TAGS
import re

pre = """from enum import Enum
class Exif(Enum):"""

rxTag = re.compile(r'^\w+$')

def pr(tag, id):
    print(f'    {tag:<30} = {id:>12}')

data = defaultdict(set)
for id, tag in TAGS.items():
    if rxTag.match(tag):
        data[tag].add(id)

print(pre)
for tag, ids in sorted(data.items(), key=lambda i: i[0].upper()):
    if len(ids) > 1:
        for n, id in enumerate(sorted(ids)):
            pr(f'{tag}{n + 1}', id)
    else:
        pr(tag, list(ids)[0])
