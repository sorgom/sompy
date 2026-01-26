"""simple progress indication"""

class ProgressWheel(object):
    def __init__(self):
        self.signs = '—\\|/'
        self.pos = 0
        self.mod = len(self.signs)

    def proceed(self):
        print(f'{self.signs[self.pos]:>3}', end="\r")
        self.pos = (self.pos + 1) % self.mod

class ProgressDots(object):
    def __init__(self, dot:str='.', width:int=40):
        self.dot = dot
        self.width = max(10, width)
        self.cnt = 0

    def proceed(self, dot=None):
        print(dot if dot else self.dot, end='', flush=True)
        self.cnt += 1
        if self.cnt == self.width:
            print()
            self.cnt = 0

class ProgressNum(object):
    def __init__(self, cap:str='count', w1:int=10, w2:int=9):
        self.cnt = 0

        def mkInfo():
            return lambda top, cont: print(f'{top:<{w1}}:{str(cont):>{w2}}')

        self.info = mkInfo()

        def mkOut():
            return lambda : print(f'{cap:<{w1}}:{self.cnt:>{w2}d}', end="\r")

        self.__out = mkOut()

    def proceed(self):
        self.cnt += 1
        self.__out()

    def back(self):
        self.cnt -= 1
        self.__out()

        # print(f'{self.cap:<{self.w1}}:{self.cnt:{self.w2}d}', end="\r")

    # def info(self, top:str, cont):
    #     print(f'{top:<{self.w1}}:{str(cont):>{self.w2}}')

    def count(self):
        return self.cnt

    def reset(self):
        self.cnt = 0

    def __gt__(self, val:int):
        return self.cnt > val

    def __lt__(self, val:int):
        return self.cnt < val

    def __ge__(self, val:int):
        return self.cnt >= val

    def __le__(self, val:int):
        return self.cnt <= val

    def __eq__(self, val:int):
        return self.cnt == val

if __name__ == '__main__':
    from time import sleep
    pg = ProgressWheel()
    for n in range(10):
        pg.proceed()
        sleep(0.1)
    print()
    pg = ProgressNum('hello', 20, 19)
    while True:
        pg.proceed()
        if pg == 10: break
        sleep(0.1)
    print()

    pg.wumpel('hello', 'world')
