"""simple progress indication"""

class ProgressWheel(object):
    def __init__(self):
        self.signs = '—\\|/'
        self.pos = 0
        self.mod = len(self.signs)

    def proceed(self):
        print(f'{self.signs[self.pos]:>3}', end="\r")
        self.pos = (self.pos + 1) % self.mod

if __name__ == '__main__':
    from time import sleep
    prw = ProgressWheel()
    for n in range(10):
        prw.proceed()
        sleep(1)
