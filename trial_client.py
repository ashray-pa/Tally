import threading
import time

a = {}

print(a)

def fun1():
    global a
    time.sleep(5)
    a[5] = 7
    print(a)

t1 = threading.Thread(target=fun1)
#t2 = threading.Thread(target=fun2)

t1.start()


