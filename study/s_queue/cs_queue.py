"""
一、queue——同步的队列类

　　queue模块实现了多生产者，多消费者的队列。当 要求信息必须在多线程间安全交换，这个模块在 线程编程时非常有用 。Queue模块实现了所有要求的锁机制。  说了半天就是Queue模块主要是多线程，保证线程安全使用的。

　　这个类实现了三种类型的queue，区别仅仅在于进去和取出的位置。在一个FIFO（First In，First Out）队列中，先加先取。在一个LIFO（Last In First Out）的队列中，最后加的先出来（操作起来跟stack一样）。priority队列，有序保存，优先级最低的先出来。

　　内部实现是在抢占式线程加上临时锁。但是没有涉及如何去处理线程的重入。

二、queue模块的内容

　　1. class queue.Queue(maxsize = 0)

　　　　构造一个FIFO队列，maxsize可以限制队列的大小。如果队列的大小达到了队列的上限，就会加锁，加入就会阻塞，直到队列的内容被消费掉。maxsize的值小于等于0，那么队列的尺寸就是无限制的

　　2. class queue.LifoQueue(maxsize = 0)

　　　　构造一个Lifo队列

　　3. class PriorityQueue(maxsize = 0)

　　　　优先级最低的先出去，优先级最低的一般使用sorted(list(entries))[0])。典型加入的元素是一个元祖(优先级, 数据)

　　4. queue.empty异常

　　　　只有非阻塞的时候，队列为空，取数据才会报异常

　　5. queue.Full异常

　　　　只有非阻塞的时候，队列满了，继续放数据才会出现异常

三、队列对象的方法：

    Queue.qsize() ：返回queue的近似值。注意：qsize>0 不保证(get)取元素不阻塞。qsize< maxsize不保证(put)存元素不会阻塞

    Queue.empty():判断队列是否为空。和上面一样注意

    Queue.full():判断是否满了。和上面一样注意

    Queue.put(item, block=True, timeout=None): 往队列里放数据。如果满了的话，blocking = False 直接报 Full异常。如果blocking = True，就是等一会，timeout必须为 0 或正数。None为一直等下去，0为不等，正数n为等待n秒还不能存入，报Full异常。

    Queue.put_nowait(item):往队列里存放元素，不等待

    Queue.get(item, block=True, timeout=None): 从队列里取数据。如果为空的话，blocking = False 直接报 empty异常。如果blocking = True，就是等一会，timeout必须为 0 或正数。None为一直等下去，0为不等，正数n为等待n秒还不能读取，报empty异常。

    Queue.get_nowait(item):从队列里取元素，不等待

    　　两个方法跟踪入队的任务是否被消费者daemon进程完全消费

    Queue.task_done()

        表示队列中某个元素被消费进程使用，消费结束发送的信息。每个get()方法会拿到一个任务，其随后调用task_done()表示这个队列，这个队列的线程的任务完成。就是发送消息，告诉完成啦！

        如果当前的join()当前处于阻塞状态，当前的所有元素执行后都会重启（意味着收到加入queue的每一个对象的task_done()调用的信息）

        如果调用的次数操作放入队列的items的个数多的话，会触发ValueError异常

    Queue.join()

        一直阻塞直到队列中的所有元素都被取出和执行

        未完成的个数，只要有元素添加到queue中就会增加。未完成的个数，只要消费者线程调用task_done()表明其被取走，其调用结束。当未完成任务的计数等于0，join()就会不阻塞


参考博客-->  https://www.cnblogs.com/skiler/articles/6977727.html
人，从刚出生来到这个世界，便开始探索这个世界。累了就歇会，精神了就继续探索，直至死亡。
"""

from queue import Queue
from threading import Thread
from multiprocessing import Queue as PQ
from multiprocessing import Process, Pool
import time


num_list = [i//i for i in range(1, 100001)]
s_list = []
m_list = []
p_list = []
q = Queue()  # 多线程队列,使用队列的好处,不用自己去给每个线程去切割分配资源.
pq = PQ()  # 多进程队列,为了避免重名,这里重命名为PQ
resp_pq = PQ()  # 计算后的多进程队列
for i in num_list:
    q.put(i)
    pq.put(i)


# =====================单线程区域===========================
def single():
    now = time.time()
    for i in num_list:
        i += 1
        s_list.append(i)
    print('单线程所用时间为{}'.format(time.time() - now))


# =====================多线程区域===========================
def many_add():
    while True:
        if q.empty():
            break
        else:
            i = q.get()
            i += 1
            m_list.append(i)
            q.task_done()


def many_thread():
    t_list = []
    for _ in range(3):
        t = Thread(target=many_add)
        t.daemon = True  # 将线程设置为守护线程,一面全部执行完,主线程还在阻塞等待.
        t_list.append(t)
    now = time.time()
    for t in t_list:
        t.start()

    q.join()  # 如果此处不写q.join()元素没有全被取完,就结束了.
    print('多线程所用时间为{}'.format(time.time() - now))


# =====================多进程区域===========================
def p_many_add(pq, resp_pq):
    while True:
        if pq.empty():
            return resp_pq
            # break
        else:
            i = pq.get()
            i += 1
            resp_pq.put(i)


def pp_mm():
    ppp_list = []
    for _ in range(3):
        p = Process(target=p_many_add, args=(pq, resp_pq,))
        p.daemon = True
        ppp_list.append(p)
    now = time.time()
    for ppp in ppp_list:
        ppp.start()
    print('多进程所用时间为{}'.format(time.time() - now))


# def pp_mm():
#     pool = Pool(3)
#     now = time.time()
#     for _ in range(3):
#         pool.apply_async(p_many_add, args=(pq, resp_pq,))
#     pool.close()
#     pool.join()
#     print('多进程所用时间为{}'.format(time.time() - now))


single()
many_thread()
pp_mm()


print(len(s_list), s_list[-1])
print(len(m_list), m_list[-1])
# print(s_list)
# print(m_list)
