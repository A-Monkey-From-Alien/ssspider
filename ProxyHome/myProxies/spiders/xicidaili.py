import time
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class XiCiDaiLi(object):

    def __init__(self):
        """西刺代理爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')

    def parser(self, total_url, xpath_str, format_url):
        total = int(etree.HTML(self.getter.rget_data(total_url)).xpath(xpath_str)[0])
        time.sleep(2)
        for pageNum in range(1, total):
            url = format_url.format(pageNum)  # 拼接url
            try:
                html = self.getter.rget_data(url)  # 访问页面
            except Exception as e:
                print("出先错误为{}".format(e))
                continue
            time.sleep(3)  # 睡两秒,防止被干掉
            soup = BeautifulSoup(html, 'lxml')
            proxy_list = soup.find('table', {'id': 'ip_list'}).find_all('tr')[1:]
            sql_list = list()
            for proxy in proxy_list:
                tmp = proxy.find_all('td')
                ip = tmp[1].get_text()
                port = tmp[2].get_text()
                lx = tmp[5].get_text().lower()
                if "socks" in lx:
                    lx = "http"
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                    self.bf.insert(ip)
                else:
                    pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)

    def run(self):
        # 国内高匿代理IP
        self.parser(
            "http://www.xicidaili.com/nn/1",
            '//div[@id="body"]/div[2]/a[last()-1]/text()',
            "http://www.xicidaili.com/nn/{}"
        )
        time.sleep(2)
        # 国内透明代理IP
        self.parser(
            "http://www.xicidaili.com/nt/1",
            '//div[@id="body"]/div[2]/a[last()-1]/text()',
            "http://www.xicidaili.com/nt/{}"
        )
        time.sleep(2)
        # HTTPS代理IP
        self.parser(
            "http://www.xicidaili.com/wn/1",
            '//div[@id="body"]/div[2]/a[last()-1]/text()',
            "http://www.xicidaili.com/wn/{}"
        )
        time.sleep(2)
        # HTTP代理IP
        self.parser(
            "http://www.xicidaili.com/wt/1",
            '//div[@id="body"]/div[2]/a[last()-1]/text()',
            "http://www.xicidaili.com/wt/{}"
        )
        self.cm.close()


if __name__ == '__main__':
    xcdl = XiCiDaiLi()
    xcdl.run()

# 无加密,直接储存.

# 西刺代理爬虫,分页,自带睡眠功能.一次爬取N多代理.
