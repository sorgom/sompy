import re
from itertools import permutations

class SunFlower(object):
    def __init__(self):
        self.outer = []
        self.choice = []
        self.result = []

        self.rules = [
            [0, [11, 0, 1], [1, 6, 5]],
            [1, [1, 2, 3], [2, 6, 0]],
            [2, [3, 4, 5], [3, 6, 1]],
            [3, [5, 6, 7], [4, 6, 2]],
            [4, [7, 8, 9], [5, 6, 3]],
            [5, [9, 10, 11], [0, 6, 4]],
            [6, [], list(range(6))]
        ]

    def subsum(self, src:list, filt:list):
        return sum([src[i] for i in filt])

    def test(self, var:list):
        ok = True
        for r, fo, fi in self.rules:
            if ok:
                ok = self.subsum(self.outer, fo) + self.subsum(var, fi) == r
        if ok:
            self.result.append(var)
    
    def get(self, num, what):
        try:
            while True:
                c = input(f'{num:2d} {what} values: ')
                r = re.findall(r'-?\d+', c)
                if len(r) == num:
                    return list(map(int, r))
        except KeyboardInterrupt:
            return []
        
    def input(self):
        self.outer = self.get(12, 'outer')
        self.choice = self.get(7, 'choice')

    def find(self):
        self.result = []
        if len(self.outer) != 12 or len(self.choice) != 7:
            return
        for p in permutations(self.choice):
            self.test(list(p))

if __name__ == '__main__':
    sf = SunFlower()
    sf.input()
    sf.find()
    print(sf.result)
