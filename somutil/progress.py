"""
simple progress indication
"""

from sys import stderr

class Progress():
    def __init__(self, *p):
        self.__cnt = 0
        self.__out = self._mkOut(*p)

    def _mkOut(self, *p):
        return lambda *p : None

    def proceed(self, n=1):
        self.__cnt += n
        self.__out(self.__cnt)

    def count(self):
        return self.__cnt

    def reset(self):
        self.__cnt = 0

    def show(self):
        self.proceed(0)

    def __gt__(self, val:int):
        return self.__cnt > val

    def __lt__(self, val:int):
        return self.__cnt < val

    def __ge__(self, val:int):
        return self.__cnt >= val

    def __le__(self, val:int):
        return self.__cnt <= val

    def __eq__(self, val:int):
        return self.__cnt == val


class ProgressWheel(Progress):
    def __init__(self):
        super().__init__()

    def _mkOut(self, *p):
        signs = '—\\|/'
        mod = len(signs)
        return lambda cnt : print(f'{signs[cnt % mod]:>3}', end="\r", file=stderr)

class ProgressDots(Progress):
    def __init__(self, width:int=40, dot:str='.'):
        super().__init__(max(5, width), dot)

    def _mkOut(self, width, dot):
        return lambda cnt : print(dot, end=('' if cnt % width else "\n"), flush=True, file=stderr)

class ProgressNum(Progress):
    def __init__(self, cap:str='count', w1:int=10, w2:int=9):
        super().__init__(cap, w1, w2)

        def mkInfo():
            return lambda top, cont: print(f'{top:<{w1}}:{str(cont):>{w2}}')

        self.info = mkInfo()

    def _mkOut(self, cap, w1, w2):
        return lambda cnt: print(f'{cap:<{w1}}:{cnt:>{w2}d}', end="\r", file=stderr)

class ProgressPercent(Progress):
    def __init__(self, total):
        super().__init__(total)

    def _mkOut(self, total):
        if total > 0:
            fac = 100 / total
            return lambda cnt: print(f'{cnt * fac:8.02f}%', end="\r", file=stderr)
        else:
            return lambda cnt: print(f'{cnt:>6}', end="\r", file=stderr)

class ProgressBar(Progress):
    def __init__(self, width:int, total):
        self.nd = -1
        super().__init__(max(8, width), total)

    def _mkOut(self, width, total):
        if total > 0:
            fac = width / total
            return lambda cnt: self.bar(width, fac, cnt)
        else:
            return lambda cnt: print(f'{cnt:>6}', end="\r", file=stderr)

    def bar(self, width, fac, cnt):
        nd = max(0, min(width, int(fac * cnt)))
        if nd != self.nd:
            print(f'   |{'=' * nd}{' ' * (width - nd)}|', end="\r", file=stderr)
            self.nd = nd

    def show(self):
        self.proceed(0)

if __name__ == '__main__':
    from time import sleep

    def test(pg:Progress):
        for n in range(15):
            pg.proceed()
            sleep(0.1)
        print()

    test(ProgressWheel())
    test(ProgressDots(10, '#'))
    pg = ProgressNum('hello', 20, 19)
    pg.show()
    sleep(1)
    test(pg)
    pg.info('done', pg.count())
    test(ProgressPercent(12))
    test(ProgressBar(20, 12))
