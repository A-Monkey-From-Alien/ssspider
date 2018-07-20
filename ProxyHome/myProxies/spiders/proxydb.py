import time
import base64
import codecs
import re
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class ProxyDB(object):

    def __init__(self):
        """ProxyDB代理的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://proxydb.net/?offset={}"

    def parser(self, page_lx):
        # page = 0
        page = 150
        while True:
            try:
                html = self.getter.rget_data(page_lx.format(page * 15))
            except Exception as e:
                print("出先错误为{}".format(e))
                continue
            time.sleep(3)  # 睡两秒,防止被干掉
            html_ele = etree.HTML(html)
            next_page = html_ele.xpath('//nav/ul/li[2]/a/@href')
            add_num = html_ele.xpath('//div[@style="display:none"]/@*')[1]
            td_list = html_ele.xpath('//table[contains(@class, "table")]/tbody/tr/td[1]/script/text()')
            lx_list = html_ele.xpath('//table[contains(@class, "table")]/tbody/tr/td[5]/text()')
            sql_list = list()
            for td in td_list:
                ip_h_reve = re.search(r"'(.*?)'.split", td).group(1)  # 提取ip头部
                ip_t_b64 = re.search(r"atob\('(.*?)'.replace", td).group(1)  # 提取base64编码部分
                p = re.search(r"pp =  \((\d+) - \(", td).group(1)  # 提取待相加的port
                ip, port = self.mk_ip_port(ip_h_reve, ip_t_b64, p, add_num)
                lx = lx_list[td_list.index(td)].strip().lower()
                if "socket" in lx:
                    lx = "http"
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

    def mk_ip_port(self, ip_h_reve, ip_t_b64, p, add_n):
        """
        将网页上抓取下来的参数,直接组织成ip和port
        :param ip_h_reve: 待翻转的ip前一部分
        :param ip_t_b64: base64加密部分的字母
        :param p: 直接抓取到的端口,需要相加
        :param add_n: 要相加的值
        :return:
        """
        l_ip_head = list(ip_h_reve)
        l_ip_head.reverse()
        ip_head = ""
        for char in l_ip_head:
            ip_head += char
        # 下面这句codecs.getdecoder("unicode_escape")(ip_t_b64)[0]超级重要.取消了转义而使用的
        ip_tail = base64.b64decode(codecs.getdecoder("unicode_escape")(ip_t_b64)[0]).decode()
        ip = ip_head + ip_tail
        port = int(p) + int(add_n)
        return ip, port

    def run(self):
        self.parser(self.url)


if __name__ == '__main__':
    pdb = ProxyDB()
    pdb.run()


# 挖槽各种加密啊, 首先显示了端口的一部分,然后进行了反转, 然后拿到16进制的字符串
# 进行解密.然后拿到假的端口,再用假的端口,加上预设值,拼接成真的端口....

# 已经解密.直接进行储存.

# 请求频繁,短暂被封, 爬多了响应会变慢,导致html提取为None.
