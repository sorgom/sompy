"""
test of object oriented multiprocessing

lessons learned:
- to access class members use Thread instead of Process
- do not use chdir - it changes directory for all threads and main
- parallel write access does not seem to cause problems
"""

from os import remove, chdir, getcwd
from os.path import join, dirname
from threading import Thread
from time import sleep

class MPOO(object):
    def __init__(self):
        self.var = 0
        self.numth = 100
        rng = range(0, self.numth)
        self.threads = [ None for n in rng]
        self.states = [ 0 for n in rng]
        self.rng = rng
        self.prefix = dirname(__file__)

    def done(self, n:int):
        self.states[n] = 0

    def isdone(self, n:int):
        return self.states[n] == 0

    def join(self, n:int):
        self.threads[n].join()
        self.threads[n] = None
        self.states[n] = 0

    def showStates(self):
        for n, c in enumerate(('free', 'busy')):
            print(f'{c:<8}:{self.states.count(n):>4}')

    def threadMethod(self, n:int):
        print(f'>>{n:>3}')
        print('currdir', n, getcwd())

        fp = join(self.prefix, f'tmp_{n:02d}.tmp')
        with open(fp, 'w') as fh:
            sleep((self.numth - n) * 0.2)
            for i in range(1, n + 1):
                print('content', i, file=fh)
            fh.close()
            remove(fp)
        chdir('..')
        print(f'<<{n:>3}')
        self.done(n)

    def getn(self):
        while True:
            self.showStates()

            for n in self.rng:
                if self.threads[n] is None:
                    return n
                if self.isdone(n):
                    self.join(n)
                    return n
            sleep(0.2)

    def start(self, n:int):
        print('start:', n)
        self.states[n] = 1
        th = Thread(target=self.threadMethod, args=(n, ))
        self.threads[n] = th
        th.start()

    def finish(self):
        print('finalizing ..')
        for th in self.threads:
            if th is not None:
                th.join()
        print('done.')


    def run(self):
        print('currdir:', getcwd())
        sleep(1)
        print('run ..')

        for i in range(0, self.numth * 3):
            n = self.getn()
            self.start(n)

        print('currdir:', getcwd())

        self.finish()

if __name__ == '__main__':
    mp = MPOO()
    mp.run()
