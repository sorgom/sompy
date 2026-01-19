"""
simple multi threading base class
provides scalable amount of threads
"""

from threading import Thread
from time import sleep
from toType import toInt

class MtBase(object):
    def __init__(self, numThreads):
        nth = max(2, toInt(numThreads, 10))
        rng = range(0, nth)
        self._threads = [ None for n in rng]
        self._states = [ 0 for n in rng]
        self._rng = rng

    def work(self, *args):
        "work method to be defined"
        pass

    def start(self, *args):
        "start working thread"
        n = self._getn()
        self._states[n] = 1
        th = Thread(target=self._tm, args=(n, *args))
        self._threads[n] = th
        th.start()

    def finalize(self):
        for th in self._threads:
            if th is not None:
                th.join()

    def numThreads(self):
        return len(self._threads)

    def _join(self, n:int):
        self._threads[n].join()
        self._threads[n] = None
        self._states[n] = 0

    def _tm(self, n:int, *args):
        self.work(*args)
        self._states[n] = 0

    def _getn(self):
        "retrieve free thread spot"
        while True:
            for n in self._rng:
                if self._threads[n] is None:
                    return n
                if self._states[n] == 0:
                    self._join(n)
                    return n
            sleep(0.1)

if __name__ == '__main__':
    class Demo(MtBase):
        "Demo class: overwrites work method"
        def __init__(self, numThreads):
            super().__init__(numThreads)
            self.name = type(self).__name__

        def info(self, *args):
            print(self.name, *args, sep=': ')

        def work(self, c:str):
            "work method overwritten"
            self.info(c, 'run..')
            sleep(2)
            self.info(c, 'done.')

        def run(self):
            "demo runtime"
            for n in range(1, 11):
                print(f'start {n:>2}')
                self.start(f'call {n + 100}')
            print('finalize')
            self.finalize()

    d = Demo(5)
    d.run()
