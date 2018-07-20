import requests
import time
from threading import Thread


def single_visit():
    resp = requests.get('https://www.baidu.com')
    print(resp.status_code)


def many_t_visit():
    t_list = []
    now = time.time()
    for _ in range(10):
        t = Thread(target=single_visit)
        # t.start()
    #     t.daemon = True
        t_list.append(t)

    for tt in t_list:
        tt.start()
    print('多线程所用时间为{}'.format(time.time() - now))

print('----------------------------单线程开始----------------------------')
now = time.time()
for _ in range(10):
    single_visit()
print('单线程所用时间为{}'.format(time.time() - now))
print('----------------------------多线程开始----------------------------')
many_t_visit()


"""
==========================↓运行结果↓==============================
----------------------------单线程开始----------------------------
200
200
200
200
200
200
200
200
200
200
单线程所用时间为1.4210920333862305
----------------------------多线程开始----------------------------
多线程所用时间为0.011373758316040039
200
200
200
200
200
200
200
200
200
200
==========================↑运行结果↑==============================
"""
