import time
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class KuaiDaiLi(object):

    def __init__(self):
        """快代理的爬虫"""
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
            time.sleep(2)  # 睡两秒,防止被干掉
            soup = BeautifulSoup(html, 'lxml')
            proxy_list = soup.find('table', {'class': 'table table-bordered table-striped'}).find('tbody')
            sql_list = list()
            for proxy in proxy_list.find_all('tr'):
                tmp = proxy.find_all('td')
                ip = tmp[0].get_text()
                port = tmp[1].get_text()
                lx = tmp[3].get_text().lower()
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                    self.bf.insert(ip)
                else:
                    pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)

    def run(self):
        # 获取国内高匿部分
        self.parser(
            "https://www.kuaidaili.com/free/inha/1/",
            '//div[@id="listnav"]/ul/li[last()-1]/a/text()',
            "https://www.kuaidaili.com/free/inha/{}/"
        )
        # 获取国内普通部分
        time.sleep(3)
        self.parser(
            "https://www.kuaidaili.com/free/intr/1/",
            '//div[@id="listnav"]/ul/li[last()-1]/a/text()',
            "https://www.kuaidaili.com/free/intr/{}/"
        )
        self.cm.close()  # 关闭数据库连接


if __name__ == '__main__':
    kdl = KuaiDaiLi()
    kdl.run()

# 无加密,直接储存.

# 快代理的爬虫,分页,自带睡眠功能.一次爬取N多代理.
