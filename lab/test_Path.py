from pathlib import Path
from os.path import dirname

p = Path(dirname(__file__))
print(p)
print(p.name)
print(len(str(p / '1')))
print(str(p / '1')[20:])

class FF_Path(Path):
    def __init__(self, *args):
        super().__init__(*args)

fp = FF_Path(dirname(__file__))

print(fp.name)
print(str(fp)[5:])
print(str(fp.absolute())[5:])
