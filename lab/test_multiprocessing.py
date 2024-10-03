from multiprocessing import Process
import time

def my_function(count=0):
    while True:
        print ("My function: {0}".format(count))
        count += 1
        time.sleep(1)

if __name__ == '__main__':
    for i in range(1, 6):
        Process(target=my_function, args=(i * 100,)).start()
    # proc2 = Process(target=my_function, args=(200,))
    # proc1.start()
    # proc2.start()
