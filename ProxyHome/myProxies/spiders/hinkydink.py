import time
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class HinkyDink(object):

    def __init__(self):
        """Hinky Dink's代理的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')

    def parser(self, total_url, xpath_str, format_url):
        total = int(etree.HTML(self.getter.rget_data(total_url)).xpath(xpath_str)[0].strip("[").strip("]"))
        time.sleep(2)
        for pageNum in range(1, total):
            if pageNum == 1:
                url = total_url
            else:
                url = format_url.format(pageNum)  # 拼接url
            try:
                html = self.getter.rget_data(url)  # 访问页面
            except Exception as e:
                print("出先错误为{}".format(e))
                continue
            time.sleep(2)  # 睡两秒,防止被干掉
            html_ele = etree.HTML(html)
            tr_list = html_ele.xpath('//table[2]//tr[2]/td[3]/table//tr/td//table//tr[@class="text"]')
            sql_list = list()
            for tr in tr_list:
                ip = tr.xpath('./td[1]/text()')[0]
                port = tr.xpath('./td[2]/text()')[0]
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, 'http'))
                    self.bf.insert(ip)
                else:
                    pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)

    def run(self):
        self.parser(
            "http://www.mrhinkydink.com/proxies.htm",  # 第一页url
            '//table[2]//tr[2]/td[3]/table//tr/td//table//tr[last()]/td/a[last()]/text()',
            "http://www.mrhinkydink.com/proxies{}.htm"  # 第二页,开始格式化的url
        )


if __name__ == '__main__':
    hd = HinkyDink()
    hd.run()

# 无加密,直接保存
