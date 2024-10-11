"""
Gimmick tool to solve the Sunflower puzzle.
Uses itertools permutations to find all possible solutions.

Sample data
- outer values: 15 -48 1 -15 1 33 -24 -30 50 -59 20 35
- choice values: 6 6 7 15 24 -12 -16
"""
import re
from itertools import permutations

class SunFlower(list[tuple]):
    """Solves the Sunflower puzzle"""
    def __init__(self):
        self.outer = None
        self.choice = None

        self.rules = (
            ((11, 0, 1), (1, 6, 5)),
            ((1, 2, 3), (2, 6, 0)),
            ((3, 4, 5), (3, 6, 1)),
            ((5, 6, 7), (4, 6, 2)),
            ((7, 8, 9), (5, 6, 3)),
            ((9, 10, 11), (0, 6, 4)),
            ((), tuple(range(6)))
        )

    def input(self):
        """input of outer values and inner choice values"""
        try:
            self.outer = self._get(12, 'outer')
            self.choice = self._get(7, 'choice')
        except KeyboardInterrupt:
            return False
        return True

    def find(self):
        """find all possible solutions"""
        self.clear()
        if not (self.outer and self.choice):
            return False
        done = set()
        for p in permutations(self.choice):
            if not p in done:
                done.add(p)
                self._test(p)
        return True

    def _subsum(self, src:tuple, sel:tuple) -> int:
        return sum([src[i] for i in sel])

    def _test(self, per:tuple):
        ok = True
        for pr, [fo, fi] in enumerate(self.rules):
            if self._subsum(self.outer, fo) + self._subsum(per, fi) != per[pr]:
                ok = False
                break
        if ok and per not in self:
            self.append(per)
    
    def _get(self, num, what) -> tuple:
        while True:
            c = input(f'{num:2d} {what} values: ')
            r = re.findall(r'-?\d+', c)
            if len(r) == num:
                return tuple(map(int, r))

if __name__ == '__main__':
    sf = SunFlower()
    if sf.input() and sf.find():
        print(*sf)
