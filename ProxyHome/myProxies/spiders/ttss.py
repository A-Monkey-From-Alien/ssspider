import time
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class ThreeThreeSixSix(object):

    def __init__(self):
        """3366代理网站的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://www.ip3366.net/?stype={}&page={}"

    def parser(self):
        for stype in range(1, 6):
            for page in range(1, 11):
                url = self.url.format(stype, page)
                time.sleep(2)
                try:
                    html = self.getter.rget_data(url)
                except Exception:
                    continue
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


if __name__ == '__main__':
    ttss = ThreeThreeSixSix()
    ttss.parser()


# 3366代理网站的爬虫,书写爬虫的时候,它说`注：免费代理为系统自动分配24小时更新一次，仅供参考。因遭受同行恶意爬虫攻击免费代理暂时关闭翻页。`
# 故,只对它进行了部分采集, 无加密, 直接采集保存.
