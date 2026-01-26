from enum import Enum, auto
from collections import Counter

class Stat(Enum):
    new = 0
    replaced = auto()
    removed = auto()
    errors = auto()

stats = Counter()

def add(v:Stat):
    stats[v.value] += 1

add(Stat.removed)
add(Stat.replaced)

print('type:', type(Stat.removed).__name__)

for n, c in [(n.value, n.name) for n in Stat]:
    print(c, stats[n])


class Wumpel:
    class ST(Enum):
        new = 0
        replaced = auto()
        removed = auto()
        errors = auto()

    def __init__(self):
        self.__stats = Counter()
        print(self.ST.removed.value)

    def add(self, s:ST):
        print('add', s.name)
        self.__stats[s.value] += 1

    def fill(self):
        for e in self.ST:
            self.add(e)
        self.add(self.ST.removed)

    def show(self):
        for n, c in [(n.value, n.name) for n in self.ST]:
            print(c, self.__stats[n])

w = Wumpel()
w.fill()
w.show()

print(Wumpel.ST.removed.value)
