from PIL import Image
from pytesseract import image_to_string
import requests
import base64
import re
from lxml import etree


class Know_Code(object):

    def __init__(self):
        """
        代码参考链接
        https://www.jianshu.com/p/365f91aea667
        sudo apt-get install tesseract-ocr
        """
        self.rep = {
            'O': '0',  # 替换列表
            'I': '1', 'L': '1',
            'Z': '2',
            'S': '8'
        }

    def initTable(self, threshold=140):
        """二值化函数"""
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        return table

    def run(self, path):
        # 1.打开图片
        im = Image.open(path)
        # 2.将彩色图像转化为灰度图
        im = im.convert('L')
        # 3.降噪，图片二值化
        binaryImage = im.point(self.initTable(), '1')
        # binaryImage.show()
        text = image_to_string(binaryImage, config='-psm 7')
        # 4.对于识别结果，常进行一些替换操作
        for r in self.rep:
            text = text.replace(r, self.rep[r])
        # 5.打印识别结果
        return text


class GetPhoto(object):

    def __init__(self):
        pass

    def parser(self):
        url = 'https://proxy.horocn.com/free-proxy.html'
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
        }
        html = requests.get(url, headers=headers)
        html_ele = etree.HTML(html.content.decode())
        photo_list = html_ele.xpath('//table/tbody/tr/th/img/@src')
        for p in photo_list:
            photo = base64.b64decode(re.search(r"data:image/jpeg;base64,(.*)", p).group(1))
            with open("./{}.jpg".format(photo_list.index(p)), "wb") as f:
                f.write(photo)


if __name__ == '__main__':
    # gp = GetPhoto()
    kc = Know_Code()
    # gp.parser()
    # for path in range(10):
    #     print(kc.run("./{}.jpg".format(path)))
    print(kc.run("./1.jpg"))
