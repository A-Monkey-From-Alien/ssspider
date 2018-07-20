from PIL import Image
from pytesseract import image_to_string


class ImagePort(object):

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

    def __initTable(self, threshold=140):
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
        binaryImage = im.point(self.__initTable(), '1')
        # binaryImage.show()
        text = image_to_string(binaryImage, config='-psm 7')
        # 4.对于识别结果，常进行一些替换操作
        for r in self.rep:
            text = text.replace(r, self.rep[r])
        # 5.打印识别结果
        return text