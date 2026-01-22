"""simple stop watch for testing"""

from datetime import datetime, timedelta

class StopWatch():
    def __init__(self):
        self.__fms = timedelta(milliseconds=1)
        self.__fs  = timedelta(seconds=1)
        self.__dt  = timedelta()
        self.start()

    def start(self):
        self.__begin = datetime.now()

    def stop(self):
        self.__dt = datetime.now() - self.__begin
        self.start()
        return self

    def inter(self):
        self.__dt = datetime.now() - self.__begin
        return self

    def __d_sec(self):
        return self.__dt / self.__fs

    def __d_ms(self):
        return self.__dt / self.__fms

    def str_sec(self):
        return f'{self.__d_sec():0.2f}  s'

    def str_ms(self):
        return f'{self.__d_ms():0.1f} ms'

    def sec(self):
        print(self.str_sec())
        return self

    def ms(self):
        print(self.str_ms())
        return self

    def dt(self):
        return self.__dt

    def avrg_str_sec(self, num:int):
        return f'{self.__d_sec() / num:0.2f}  s' if num > 0 else '--'

    def avrg_str_ms(self, num:int):
        return f'{self.__d_ms() / num:0.2f} ms' if num > 0 else '--'

    def avrg_sec(self, num:int):
        print(self.avrg_str_sec(num))
        return self

    def avrg_ms(self, num:int):
        print(self.avrg_str_ms(num))
        return self
if __name__ == '__main__':
    from time import sleep

    sw = StopWatch()
    sleep(0.1231)
    sw.stop().ms()
    sleep(1.36)
    sw.stop().sec()
    sleep(1.34)
    sw.stop().sec().avrg_ms(200)
