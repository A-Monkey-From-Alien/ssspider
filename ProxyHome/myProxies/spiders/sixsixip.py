import time
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class SixSixIP(object):

    def __init__(self):
        """66ip代理的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://www.66ip.cn/{}.html"

    def run(self):
        total = int(etree.HTML(self.getter.rget_data("http://www.66ip.cn/1.html")).xpath('//div[@id="PageList"]/a[last()-1]/text()')[0])
        time.sleep(3)
        # for pageNum in range(1, total):
        # for pageNum in range(1176, total):
        for pageNum in range(1200, total):
            url = self.url.format(pageNum)  # 拼接url
            try:
                html = self.getter.rget_data(url)  # 访问页面
            except Exception as e:
                print("出先错误为{}".format(e))
                continue
            time.sleep(3)  # 睡两秒,防止被干掉
            soup = BeautifulSoup(html, 'lxml')
            proxy_list = soup.find('table', {"border": "2px"})
            sql_list = list()
            for proxy in proxy_list.find_all('tr')[1:]:
                ip = proxy.find_all('td')[0].get_text()  # 获取ip
                port = proxy.find_all('td')[1].get_text()  # 获取端口
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, 'http'))
                    self.bf.insert(ip)
                else:
                    pass
            for sql in sql_list:  # 一次性操作数据库)
                self.cm.exe(sql)
        self.cm.close()


if __name__ == '__main__':
    ss = SixSixIP()
    ss.run()

# 无加密,直接储存.

# 66ip代理网 分页,自带睡眠功能.一次爬取N多代理.
# 哎呦我曹,辣鸡网站,1176.页面错误了.  往后辣鸡页面较多,代理也比较完犊子.
