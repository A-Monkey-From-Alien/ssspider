import time
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class ListProxy(object):

    def __init__(self):
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}"

    def parser(self):
        total = int(etree.HTML(self.getter.rget_data(self.url.format(1))).xpath('//div[@id="page"]/table[3]/tr/td[1]/a[last()]/text()')[0].strip('[').strip(']'))
        time.sleep(3)
        for pageNum in range(1, total):
            url = self.url.format(pageNum)  # 拼接url
            try:
                html = self.getter.rget_data(url)  # 访问页面
            except Exception as e:
                print("出先错误为{}".format(e))
                continue
            time.sleep(3)  # 睡两秒,防止被干掉
            soup = BeautifulSoup(html, 'lxml')
            proxy_list = soup.find("table", 'bg').find_all('tr')
            sql_list = list()
            for proxy in proxy_list:
                tmp = proxy.find_all("td")
                if tmp:
                    ip = tmp[1].get_text()
                    port = tmp[2].get_text()
                    lx = tmp[6].get_text()
                    if lx == "yes":
                        lx = 'https'
                    else:
                        lx = 'http'
                    if not self.bf.isContains(ip):
                        sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                        self.bf.insert(ip)
                    else:
                        pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)
        self.cm.close()


if __name__ == '__main__':
    lp = ListProxy()
    lp.parser()

# 无加密,直接保存.

# Proxy List + 的爬虫,分页,自带睡眠功能.一次爬取N多代理.
