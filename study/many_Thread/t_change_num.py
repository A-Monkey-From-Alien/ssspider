import time
import threading

# 假定这是你的银行存款:
now = time.time()
balance = 0


def change_it(n):
    # 先存后取，结果应该为0:
    global balance
    balance = balance + n
    balance = balance - n


def run_thread(n):
    for i in range(10000000):  # 1000万次
        change_it(n)


t1 = threading.Thread(target=run_thread, args=(5,))
t2 = threading.Thread(target=run_thread, args=(8,))
t1.start()
t2.start()
t1.join()
t2.join()
print("加锁前~↓")
print(balance)
print('总用时为%s' % (time.time() - now))

# --------------------------华丽的分隔符--------------------------------
add_mutex_time = time.time()
# 加锁后~ 创建一把互斥锁
mutex = threading.Lock()
balance = 0  # 由于上面的代码将balance改坏了,故重新赋值为0,不进行注释,以此进行对比.


def run_thread_mutex(n):
    for i in range(10000000):
        # 先要获取锁:
        mutex.acquire()
        try:
            # 放心地改吧:
            change_it(n)
        finally:
            # 改完了一定要释放锁:
            mutex.release()


t3 = threading.Thread(target=run_thread_mutex, args=(5,))
t4 = threading.Thread(target=run_thread_mutex, args=(8,))
t3.start()
t4.start()
t3.join()
t4.join()
print("加锁后~↓")
print(balance)
print("加锁后总用时%s" % (time.time() - add_mutex_time))


"""
加锁前~↓
22
总用时为2.316227912902832
加锁后~↓
0
加锁后总用时16.477405548095703
"""
