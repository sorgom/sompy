from multiprocessing import Process
from os import environ
from time import sleep

def prEnv(var, who):
    """print environment variable"""
    print(var, who, environ.get(var, 'NN'))

def my_function(nr:int):
    prEnv('wumpel', nr)
    prEnv('rumpel', nr)
    sleep(1)
    environ['wumpel'] = str(nr)
    sleep(1)
    prEnv('wumpel', nr)
    sleep(1)

if __name__ == '__main__':
    procs = []
    environ['rumpel'] = 'MAIN RUMPEL'
    for i in range(1, 6):
        proc = Process(target=my_function, args=(i,))
        procs.append(proc)
        proc.start()
        # print(f'-> {i} pid {proc.pid}')
        sleep(0.10)
    sleep(2)
    prEnv('wumpel', 'main')
    for proc in procs:
        proc.join()
    print('joined.')
