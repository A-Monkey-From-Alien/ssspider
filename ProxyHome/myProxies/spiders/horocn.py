import time
import re
import os
import base64
from lxml import etree
from Tools.tool_requests.getter import GETTER
from Tools.DataBase.db import ConnMysql
from Tools.BloomFilterOnRedis import BloomFilter
from Tools.ImagePort import ImagePort


class Horocn(object):

    def __init__(self):
        """
        蜻蜓代理的爬虫
        https://proxy.horocn.com/free-proxy.html?page={}
        """
        self.getter = GETTER(rtimes=10)
        self.cm = ConnMysql()
        self.bf = BloomFilter(key='allip')
        self.img = ImagePort()
        self.port = "12345"
        self.url = "https://proxy.horocn.com/free-proxy.html?page={}"

    def parser(self):
        # page = 1
        page = 3000
        while True:
            try:
                html = self.getter.rget_data(self.url.format(page))
            except Exception as e:
                print("出现错误为{}".format(e))
                continue
            time.sleep(2)  # 睡两秒,防止被干掉
            html_ele = etree.HTML(html)
            next_page = html_ele.xpath('//ul[@class="pager"]//a[text()="下一页 →"]/@href')[0]
            tr_list = html_ele.xpath('//table/tbody/tr')
            sql_list = list()
            path_list = list()
            for tr in tr_list:
                ip = tr.xpath('./th[1]/text()')[0]
                # 开始保存图片
                base_port_image = tr.xpath('./th[2]/img/@src')[0]
                photo = base64.b64decode(re.search(r"data:image/jpeg;base64,(.*)", base_port_image).group(1))
                path = "./{}.jpg".format(tr_list.index(tr))
                path_list.append(path)  # 将其放入列表一次性操作
                with open(path, "wb") as f:
                    f.write(photo)
                for times in range(10):
                    try:
                        self.port = int(self.img.run(path))
                    except Exception:
                        continue
                    else:
                        break
                # 校验是否已有
                if not self.bf.isContains(ip):
                    sql_list.append("""INSERT INTO allip (`ip`, `port`, `type`) VALUES ('{}', '{}', '{}')""".format(ip, self.port, "http"))
                    self.bf.insert(ip)
                else:
                    pass
            for path in path_list:
                os.remove(path)
            for sql in sql_list:  # 一次性操作数据库
                self.cm.exe(sql)
            if next_page != "javascript:;":
                page += 1
            else:
                break


if __name__ == '__main__':
    h = Horocn()
    h.parser()

# 优质ip, 更新速度比较快, 但端口通过base64的图片加密了,已经破解,但识别率不太好.
