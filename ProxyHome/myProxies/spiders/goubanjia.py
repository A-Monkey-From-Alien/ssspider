from bs4 import BeautifulSoup
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class GouBanJia(object):

    def __init__(self):
        """全网代理IP的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "http://www.goubanjia.com/"

    def parser(self):
        """
        ↓此函数借鉴于↓
        https://blog.csdn.net/weixin_37586648/article/details/78868015
        """
        html = self.getter.rget_data(self.url)
        # 解析html
        soup = BeautifulSoup(html, "lxml")
        # ---------↓自己添加获取类型↓---------
        lx_list = list()
        ip_port_list = list()
        for tr in soup.find_all('tr'):
            temp = tr.find_all('td')
            if temp:
                lx = temp[2].get_text()
                lx_list.append(lx)
        # ---------↑自己添加获取类型↑---------
        # 获取所有的ip的td
        td_list = soup.select('td[class="ip"]')
        for td in td_list:
            # 获取当前td所以的子标签
            child_list = td.find_all()
            ip_port = ""
            for child in child_list:
                if 'style' in child.attrs.keys():
                    if child.attrs['style'].replace(' ', '') == "display:inline-block;":
                        if child.string is not None:
                            ip_port = ip_port + child.string
                # 过滤出端口号
                elif 'class' in child.attrs.keys():
                    class_list = child.attrs['class']
                    if 'port' in class_list:
                        port = self.mk_port(class_list[1])
                        # 拼接端口
                        ip_port = ip_port + ":" + str(port)
                else:
                    if child.string is not None:
                        ip_port = ip_port + child.string
            # 接下来是我自己的
            ip_port_list.append(ip_port)
        return lx_list, ip_port_list

    def run(self):
        lx_list, ip_port_list = self.parser()
        sql_list = list()
        for ip_port in ip_port_list:
            lx = lx_list[ip_port_list.index(ip_port)]
            ip = ip_port.split(":")[0]
            port = ip_port.split(":")[1]
            # 对ip进行布隆去重
            if not self.bf.isContains(ip):
                sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, lx))
                self.bf.insert(ip)
            else:
                pass
        for sql in sql_list:  # 一次性操作数据库
            self.cm.exe(sql)
        self.cm.close()  # 关闭数据库连接

    def mk_port(self, port_word):
        word = list(port_word)
        num_list = []
        for item in word:
            num = 'ABCDEFGHIZ'.find(item)
            num_list.append(str(num))
        port = int("".join(num_list)) >> 0x3
        return port


if __name__ == '__main__':
    gbl = GouBanJia()
    gbl.run()

# ip和端口都被加密了....已破解

# 全网代理IP的爬虫,可短时间内刷新,其网址单一,但是更新频率较快.每3-5分钟请求一次
