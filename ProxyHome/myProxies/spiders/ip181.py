from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter
import json


class IP181(object):

    def __init__(self):
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = 'http://www.ip181.com/'

    def parser(self):
        js_data = self.getter.rget_data(self.url)
        sql_list = list()  # 一次性操作数据库
        for proxy in json.loads(js_data).get("RESULT"):
            ip = proxy.get('ip')
            port = proxy.get('port')
            if not self.bf.isContains(ip):
                sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, 'http'))
                self.bf.insert(ip)
            else:
                pass
        for sql in sql_list:  # 一次性操作数据库
            self.cm.exe(sql)
        self.cm.close()  # 关闭数据库连接


if __name__ == '__main__':
    ip181 = IP181()
    ip181.parser()

# 直接返回,无加密

# 此爬虫可短时间内刷新,其网址单一,但是更新频率一般,响应速度也比较慢,每30分钟请求一次
