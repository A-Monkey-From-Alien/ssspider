from bs4 import BeautifulSoup
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class Data5U(object):

    def __init__(self):
        """data5u代理的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://www.data5u.com/free/index.shtml"

    def parser(self):
        html = self.getter.rget_data(self.url)
        soup = BeautifulSoup(html, "lxml")
        proxy_list = soup.find_all('ul', {'class': "l2"})
        sql_list = list()  # 一次性操作数据库
        for proxy in proxy_list:
            tmp = proxy.find_all('li')
            ip = tmp[0].get_text()
            port_zimu = list(tmp[1].attrs.values())[0][1]
            lx = tmp[3].get_text()
            port = self.mk_port(port_zimu)
            # 对ip进行布隆去重
            if not self.bf.isContains(ip):
                sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                self.bf.insert(ip)
            else:
                pass
        for sql in sql_list:  # 一次性操作数据库
            self.cm.exe(sql)
        self.cm.close()  # 关闭数据库连接

    def mk_port(self, port_word):
        word = list(port_word)
        num_list = []
        for item in word:
            num = 'ABCDEFGHIZ'.find(item)
            num_list.append(str(num))
        port = int("".join(num_list)) >> 0x3
        return port


if __name__ == '__main__':
    d5 = Data5U()
    d5.parser()

# 端口被加密了....已破解

# 此爬虫可短时间内刷新,其网址单一,但是更新频率较快.每3-5分钟请求一次
