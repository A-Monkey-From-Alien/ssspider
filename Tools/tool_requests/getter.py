from Tools.tool_requests.ua_pool import UA
import requests
from retrying import retry


"""
时间:2018年7月2日
作者:alien
版本: Python3 + requests
说明:页面请求相关功能
"""


class GETTER(object):
    """发送页面请求"""

    def __init__(self, use_proxy='NO', ua_type='PC', rtimes=3):
        """
        初始化一个getter对象,选择该对象是否使用代理,以及随机的请求头,等~.
        :param use_proxy: 是否使用代理  -->供选参数'YES'或'NO'
        :param ua_type: 随机请求头类型 -->供选参数'PC'或'PHONE'或'NO'
        :param rtimes: 请求失败重试次数
        """
        self.ua = UA()
        self.use_proxy = use_proxy
        self.ua_type = ua_type
        self.PROXIES = {}
        self.rtimes = rtimes
        self.HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.USER_AGENT = ''

    def __ua_dl(self):
        """
        用以实现每调用一次请求方法,就实现生成一次随机的请求头和代理
        :return: 修改默认的`self.USER_AGENT`和`self.PROXIES`
        """
        # ==============处理ua部分==============
        if self.ua_type == 'PC':  # 调取电脑版User-Agent
            self.USER_AGENT = self.ua.pc_ua()
        elif self.ua_type == 'PHONE':  # 调取手机版User-Agent
            self.USER_AGENT = self.ua.phone_ua()
        else:
            print("温馨提示：您没有使用随机的User-Agent ☺")
            pass  # else就是不使用随机的User-Agent或者settings参数填错了.
        # ==============处理代理部分==============
        if self.use_proxy == 'YES':
            # 选择使用代理,获取随机代理一枚 requests需求为eg:--> {"http": "http://120.77.173.13:80"}
            pass  # 暂时设置为pass 就是都不使用,待代理模块做完了再添加进来
        else:
            print("温馨提示：您没有使用随机的代理 ☺")
            pass  # else就是不使用代理,或者参数填错了.

    def get_data(self, url, decode_type='utf-8', proxies=None, **kwargs):
        """
        发送修改后的get请求.
        :param proxies: 代理
        :param url: 目标地址
        :param decode_type:　解码类型
        :param kwargs: get请求可传递的其他参数
        :return: 解码后的数据
        """
        self.__ua_dl()  # 调用ua_dl方法,生成随机的请求头和代理.修改self属性
        headers = {"User-Agent": self.USER_AGENT}
        if proxies:
            pass
        else:
            proxies = self.PROXIES
        response = requests.get(url=url, headers=headers, proxies=proxies, **kwargs)
        try:
            result = response.content.decode(decode_type)
        except Exception:
            result = response.text
        return result

    def post_data(self, url, data, decode_type='utf-8', proxies=None, **kwargs):
        """
        发送修改后的post请求.
        :param proxies: 代理
        :param url: 目标地址
        :param data: post请求需要携带的参数
        :param decode_type: 解码类型
        :param kwargs: post请求可传递的其他参数
        :return: 解码后的数据
        """
        self.__ua_dl()  # 调用ua_dl方法,生成随机的请求头和代理.修改self属性
        headers = {"User-Agent": self.USER_AGENT}
        if proxies:
            pass
        else:
            proxies = self.PROXIES
        response = requests.post(url=url, data=data, headers=headers, proxies=proxies, **kwargs)
        try:
            result = response.content.decode(decode_type)
        except Exception:
            result = response.text
        return result

    def __re_times(self):
        return self.rtimes

    @retry(stop_max_attempt_number=__re_times)
    def rget_data(self, url, decode_type='utf-8', proxies=None, **kwargs):
        return self.get_data(url=url, decode_type=decode_type, proxies=proxies, **kwargs)

    @retry(stop_max_attempt_number=__re_times)
    def rpost_data(self, url, data, decode_type='utf-8', proxies=None, **kwargs):
        return self.post_data(url=url, data=data, decode_type=decode_type, proxies=proxies, **kwargs)
