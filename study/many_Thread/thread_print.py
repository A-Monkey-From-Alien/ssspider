import threading
import time


# 新线程执行的代码:
def loop():
    print('thread %s is running...' % threading.current_thread().name)
    n = 0
    while n < 5:
        n = n + 1
        print('thread %s >>> %s' % (threading.current_thread().name, n))
        time.sleep(1)
    print('thread %s ended.' % threading.current_thread().name)


print('thread %s is running...' % threading.current_thread().name)
t_list = []
t = threading.Thread(target=loop, name='LoopThread')
t2 = threading.Thread(target=loop, name='LoopThread2')
t_list.append(t)
t_list.append(t2)
now = time.time()
# for i in t_list:
#     i.start()
#
# for j in t_list:
#     j.join()
"""
两个for循环等价于这样的代码片段
t2.start()
t.start()
注意和下面未注释的区别~!(顺序)
t2.join()
t.join()
"""
# print(time.time() - now)  # 5.004679441452026

t2.start()
t2.join()
t.start()
t.join()
print(time.time() - now)  # 10.012069463729858
print('thread %s ended.' % threading.current_thread().name)

"""
综上所述,需要注意的是,多线程创建后,同时启动,才能起到多线程的作用.代码由上到下执行,同时start,同时join.
不能一个join后另一个start
"""