from os import environ
from sys import argv
from time import sleep

environ['wumpel'] = argv[1]
for i in range(5):
    sleep(1)
    print('Process', environ.get('wumpel', 'NN'), i)
