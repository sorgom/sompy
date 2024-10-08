import re
from itertools import permutations

class SunFlower(object):
    def __init__(self):
        self.outer = []
        self.choice = []
        self.result = []

        self.rules = [
            [[11, 0, 1], [1, 6, 5]],
            [[1, 2, 3], [2, 6, 0]],
            [[3, 4, 5], [3, 6, 1]],
            [[5, 6, 7], [4, 6, 2]],
            [[7, 8, 9], [5, 6, 3]],
            [[9, 10, 11], [0, 6, 4]],
            [[], list(range(6))]
        ]

    def subsum(self, src:list, sel:list):
        return sum([src[i] for i in sel])

    def test(self, per:list):
        ok = True
        for pr, [fo, fi] in enumerate(self.rules):
            if ok:
                ok = self.subsum(self.outer, fo) + self.subsum(per, fi) == per[pr]
        if ok and per not in self.result:
            self.result.append(per)
    
    def get(self, num, what):
        while True:
            c = input(f'{num:2d} {what} values: ')
            r = re.findall(r'-?\d+', c)
            if len(r) == num:
                return list(map(int, r))
        
    def input(self):
        try:
            self.outer = self.get(12, 'outer')
            self.choice = self.get(7, 'choice')
        except KeyboardInterrupt:
            return False

    def find(self):
        self.result = []
        if len(self.outer) != 12 or len(self.choice) != 7:
            return False
        for p in permutations(self.choice):
            self.test(list(p))
        return True

if __name__ == '__main__':
    sf = SunFlower()
    if sf.input() and sf.find():
        print(sf.result)

# sample data
# outer values: 15 -48 1 -15 1 33 -24 -30 50 -59 20 35
# choice values: 6 6 7 15 24 -12 -16