import time
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class MiMi(object):

    def __init__(self):
        """秘密代理的IP抓取"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = [
            "http://www.mimiip.com/gngao/{}",  # 高匿代理IP
            "http://www.mimiip.com/gnpu/{}",  # 普匿代理IP
            "http://www.mimiip.com/gntou/{}",  # 透明代理IP
            "http://www.mimiip.com/hw/{}"  # 国外代理IP
        ]

    def parser(self, page_lx):
        page = 1
        while True:
            try:
                html = self.getter.rget_data(page_lx.format(page))
            except Exception as e:
                print("出先错误为{}".format(e))
                continue
            time.sleep(2)  # 睡两秒,防止被干掉
            next_page = etree.HTML(html).xpath('//div[@class="pagination"]//*[text()="下一页 ›"]/@href')
            soup = BeautifulSoup(html, 'lxml')
            proxies_list = soup.find('table', 'list').find_all('tr')
            sql_list = list()
            for proxy in proxies_list:
                temp = proxy.find_all('td')
                if temp:
                    # 获取ip
                    ip = temp[0].get_text()
                    # 获取端口
                    port = temp[1].get_text()
                    # 获取类型
                    lx = temp[4].get_text().lower()
                    # 校验是否已有
                    if not self.bf.isContains(ip):
                        sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                        self.bf.insert(ip)
                    else:
                        pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)
            if next_page:
                page += 1
            else:
                break

    def run(self):
        for page_lx in self.url:
            time.sleep(2)
            self.parser(page_lx)


if __name__ == '__main__':
    mm = MiMi()
    mm.run()

# 秘密代理的爬去,无加密直接储存 爬多了,会被封的.
