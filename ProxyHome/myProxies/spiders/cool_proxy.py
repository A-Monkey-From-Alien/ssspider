import time
import re
import base64
from bs4 import BeautifulSoup
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter


class CoolProxy(object):

    def __init__(self):
        """cool-proxy.net代理的爬虫"""
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.url = "https://www.cool-proxy.net/proxies/http_proxy_list/sort:score/direction:desc/page:{}"

    def parser(self):
        page = 1
        while True:
            try:
                html = self.getter.rget_data(self.url.format(page))
            except Exception as e:
                print("出现错误为{}".format(e))
                continue
            time.sleep(2)  # 睡两秒,防止被干掉
            next_page = etree.HTML(html).xpath('//table//tr[last()]//span[last()]/a')
            soup = BeautifulSoup(html, 'lxml')
            tr_list = soup.find('table').find_all('tr')
            sql_list = list()
            for tr in tr_list:
                temp = tr.find_all('td')
                if temp:
                    try:
                        ip = self.mk_ip(re.search(r"str_rot13\(\"(.*?)\"\)", temp[0].find('script').get_text()).group(1))
                    except Exception:
                        continue  # 里面有混淆的tr
                    port = temp[1].get_text()
                    # 校验是否已有
                    if not self.bf.isContains(ip):
                        sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, port, "http"))
                        self.bf.insert(ip)
                    else:
                        pass
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)
            if next_page:
                page += 1
            else:
                break

    def mk_ip(self, en_ip):
        """
        将拿到的-->`ZGH5Ywt5YwVlBF42At==`这种ip解码成可用ip-->159.89.229.66
        :param en_ip:爬取到的加密ip
        :return:解密后的ip
        """
        letter_str = ""
        for char in en_ip:
            if char in "0123456789==":  # 数字和等号用来混淆,直接拼接
                letter_str += char
            else:
                head = ord(char[0])  # 获得该字母的Unicode的编码
                tail = 13 if char.lower() < 'n' else -13  # 盐
                letter_str += chr(head + tail)  # 讲加密后的值解析成字母并拼接
        return base64.b64decode(letter_str).decode()  # base64解码拼接后的字符串


if __name__ == '__main__':
    cp = CoolProxy()
    cp.parser()

# 尼大爷的, 这ip加密的,真是没谁了. 已破解, 更新速度快,代理量大.
# 优秀代理网站.
