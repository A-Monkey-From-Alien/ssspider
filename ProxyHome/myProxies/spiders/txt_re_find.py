#!/home/alien/.local/virtualenvs/spider/bin/python
# -*- coding:utf-8 -*-
"""#!/bin/python"""
import re
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter
"""
时间:2018年6月29日
作者:alien
版本: Python3 + requests
说明:requests爬虫爬取IP
"""


class TXTIPPage(object):

    def __init__(self):
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url_list = [
            'https://www.rmccurdy.com/scripts/proxy/output/http/ALL',
            'https://www.rmccurdy.com/scripts/proxy/output/socks/ALL',
            'https://www.rmccurdy.com/scripts/proxy/proxylist.txt',
            'http://www.proxylists.net/http_highanon.txt',
            'http://ab57.ru/downloads/proxyold.txt'
        ]

    def run(self):
        for url in self.url_list:
            data = self.getter.rget_data(url)
            ip_list = re.findall('\d+\.\d+\.\d+\.\d+:\d+', data)
            temp_l = [[ipport.split(":")[0], ipport.split(":")[1]] for ipport in ip_list]
            sql_list = list()
            for temp in temp_l:
                ip = temp[0]
                port = temp[1]
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, 'http'))
                    self.bf.insert(ip)
                else:
                    pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)
        self.cm.close()


if __name__ == '__main__':
    txt_ip = TXTIPPage()
    txt_ip.run()

# 无加密,直接储存.

# 这几个网站比较舒服~直接返回txt的ip与端口, 直接保存没毛病.
