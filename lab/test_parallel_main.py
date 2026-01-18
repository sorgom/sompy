from os import environ
from os.path import dirname
from subprocess import Popen
from sys import executable
from time import sleep

sub_script = f'{dirname(__file__)}/test_parallel_sub.py'

procs = []
for i in range(5):
    proc = Popen([executable, sub_script, str(i)])
    procs.append(proc)
    print(f'Started process {i} with PID {proc.pid}')

sleep(1)
print(environ.get('wumpel', 'NN'))
sleep(1)
print(environ.get('wumpel', 'NN'))
for proc in procs:
    proc.wait()

print('All processes have finished.')
