import time
import re
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class YouDaiLi(object):

    def __init__(self):
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://www.youdaili.net/Daili/http/"

    def parser(self):
        url = etree.HTML(self.getter.rget_data(self.url)).xpath('//div[@class="chunlist"]/ul/li[1]/p/a/@href')[0]
        time.sleep(2)
        html = self.getter.rget_data(url)
        soup = BeautifulSoup(html, 'lxml')
        p_tag = soup.find_all('p')
        sql_list = list()
        for p in p_tag:
            ip_list = re.findall('(.*?)    ————    (.*?)    ————    (.*?)    ————    (.*?)    ', p.get_text())
            if ip_list:
                # [('61.130.226.39', '20753', '浙江湖州', 'HTTPS')]
                ip = ip_list[0][0]
                port = ip_list[0][1]
                lx = ip_list[0][3]
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                    self.bf.insert(ip)
                else:
                    pass
        for sql in sql_list:  # 一次性操作数据库
            # print(sql)
            self.cm.exe(sql)
        self.cm.close()


if __name__ == '__main__':
    ydl = YouDaiLi()
    ydl.parser()

# 无加密,直接储存.

# 有代理网站的爬虫, 更新极度缓慢, 但是代理质量还行, 可记录后自行更新.
