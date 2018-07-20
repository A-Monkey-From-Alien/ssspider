from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class ThreeFourSixFour(object):

    def __init__(self):
        """3464网站的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://www.3464.com/data/Proxy/http/"

    def parser(self):
        html = self.getter.rget_data(self.url)
        html_ele = etree.HTML(html)
        tr_list = html_ele.xpath('//div[@class="CommonBody"]/table[6]//table//tr')[1:]
        sql_list = list()
        for tr in tr_list:
            try:
                ip = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
            except Exception:
                continue
            # 校验是否已有
            if not self.bf.isContains(ip):
                sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, "http"))
                self.bf.insert(ip)
            else:
                pass
        for sql in sql_list:  # 一次性操作数据库
            self.cm.exe(sql)


if __name__ == '__main__':
    tfsf = ThreeFourSixFour()
    tfsf.parser()

# 垃圾代理网站, 无加密.全透明,看着爬吧
# 直接保存
