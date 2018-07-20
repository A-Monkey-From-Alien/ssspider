from Tools.CheckIP import CheckIP
import time
import requests
import re

# 多线程
# ip_list = [{"http": "http://39.104.77.198:8080"}, {"http": "http://202.183.201.7:8081"}, {"http": "http://74.208.123.225:3128"}, {"http": "http://187.125.106.234:8080"}, {"https": "https://59.39.63.142:8181"}]
# 单线程
# ip_list = [{"http": "http://151.80.88.45:3128"}, {"http": "http://203.189.152.195:8080"}, {"http": "http://177.201.67.107:3128"}, {"http": "http://187.76.206.50:8080"}, {"http": "http://218.60.8.98:3129"}, {"http": "http://36.250.87.88:8102"}, {"http": "http://163.172.28.22:80"}]
# ip_list = [{"http": "http://201.55.32.151:9999"}, {"http": "http://40.132.242.226:3128"}, {"https": "https://123.139.56.238:9999"}, {"http": "http://186.46.168.42:8080"}, {"http": "http://85.185.238.214:8080"}]
# ip_list = [{"http": "http://46.101.0.138:8080"}, {"http": "http://190.1.137.102:3128"}, {"http": "http://178.211.163.102:53281"}, {"http": "http://96.9.69.164:53281"}, {"http": "http://103.59.212.93:8080"}]

# 多线程
# now = time.time()
# ci = CheckIP(proxies_list=ip_list)
# ci.check_ip_many_thread()
# print(time.time() - now)
# 11.250531911849976

# 单线程
# now = time.time()
# ci = CheckIP()
# for i in ip_list:
#     print(ci.check_ip_single(i))
# print(time.time() - now)
# 22.245927333831787

# 多多的往库里面增加IP用来校验
# now = time.time()
# ci = CheckIP(proxies_list=ip_list, baba_url="https://www.baidu.com", judgeScore=0, check_list=["https://www.baidu.com"])
# ci.check_ip_many_thread()
# print(time.time() - now)

# 从数据库中查询出来ip进行二次校验.不合格的就删掉.
# 单线程
# ci = CheckIP()
# ci.recheck_single()
# 多线程
# ci = CheckIP()
# ci.recheck_many_thread()


# 切割字典类型ip还原成, 类型, ip, 端口
# def sp_proxies(proxies):
#     try:
#         str_ip = proxies["http"]
#     except Exception:
#         str_ip = proxies["https"]
#     l_ip = re.split(':', str_ip)
#     lx = l_ip[0]
#     ip = l_ip[1].strip("//")
#     port = l_ip[2]
#     return lx, ip, port
# for i in ip_list:
#     print(sp_proxies(i))

