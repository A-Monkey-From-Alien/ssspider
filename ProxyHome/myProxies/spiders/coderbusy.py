import time
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class CoderBusy(object):

    def __init__(self):
        """码农很忙代理爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = [
            'https://proxy.coderbusy.com/',  # 首页
            'https://proxy.coderbusy.com/classical/https-ready.aspx?page={}',  # HTTPS代理
            'https://proxy.coderbusy.com/classical/post-ready.aspx?page={}',  # 支持POST的代理
            'https://proxy.coderbusy.com/classical/anonymous-type/transparent.aspx?page={}',  # 透明代理
            'https://proxy.coderbusy.com/classical/anonymous-type/anonymous.aspx?page={}',  # 匿名代理
            'https://proxy.coderbusy.com/classical/anonymous-type/highanonymous.aspx?page={}',  # 高匿代理
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
            next_page = etree.HTML(html).xpath('//nav[@class="text-center"]/ul/li[@title="下一页"]/a/@href')
            soup = BeautifulSoup(html, 'lxml')
            proxies_list = soup.find('table', 'table').find_all('tr')
            sql_list = list()
            for proxy in proxies_list:
                temp = proxy.find_all('td')
                if temp:
                    # 获取ip
                    ip = temp[0].get_text().strip()
                    # 获取端口
                    port = int(temp[2].get("data-i"))
                    for num in ip.split('.'):
                        port -= int(num)
                    # 获取类型
                    if temp[8].find('i'):
                        lx = 'https'
                    else:
                        lx = 'http'
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
    cb = CoderBusy()
    cb.run()

# 挖槽,码农很忙的代理骚啊  端口做加密处理了,已经破解
# 端口与类型 https/ http的校验


# 完成码农代理的ip抓取,多个模块间可能会有重复抓取的ip,但是去重已经实现,
# 分页,自带睡眠功能.一次爬取N多代理.
