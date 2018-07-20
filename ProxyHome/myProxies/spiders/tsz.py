import time
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class ThreeSixZero(object):

    def __init__(self):
        """360代理的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = [
            "http://www.swei360.com/free/?page={}",  # 国内高匿代理
            "http://www.swei360.com/free/?stype=2&page={}",  # 国内普通代理
            "http://www.swei360.com/free/?stype=3&page={}",  # 国外高匿代理
            "http://www.swei360.com/free/?stype=4&page={}"  # 国外普通代理
        ]

    def parser(self, format_url):
        for pageNum in range(1, 8):  # 他只有7页
            url = format_url.format(pageNum)  # 拼接url
            try:
                html = self.getter.rget_data(url)  # 访问页面
            except Exception as e:
                print("出现错误为{}".format(e))
                continue
            time.sleep(2)  # 睡两秒,防止被干掉
            html_ele = etree.HTML(html)
            tr_list = html_ele.xpath('//table/tbody/tr')
            sql_list = list()
            for tr in tr_list:
                ip = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
                lx = tr.xpath('./td[4]/text()')[0]
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                    self.bf.insert(ip)
                else:
                    pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)

    def run(self):
        for format_url in self.url:
            time.sleep(2)
            self.parser(format_url)


if __name__ == '__main__':
    thz = ThreeSixZero()
    thz.run()

# 360代理的爬虫,无加密,直接保存
