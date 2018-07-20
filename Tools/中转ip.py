from Tools.CheckIP import CheckIP
from Tools.DataBase.db import ConnMysql
import json


ci = CheckIP()
cm = ConnMysql()


IP_LIST = []
sql = """select `type`, `ip`, `port` from ipipip where nmd='High Anonymity' and score='100';"""
cm.exe(sql)
for data in cm.cursor:
    proxies = ci.mk_proxies(data[0], data[1], data[2])
    print(proxies)
    IP_LIST.append(proxies)
    print(IP_LIST)


with open('ip_pool.py', 'w') as f:
    f.write('IP_LIST = ' + json.dumps(IP_LIST))
