#!/bin/python
# -*- coding:utf-8 -*-
import requests
# import time
import re
import json
from queue import Queue
from threading import Thread
from Tools.BloomFilterOnRedis import BloomFilter
from Tools.tool_requests.ua_pool import UA
from Tools.DataBase.db import ConnMysql


class CheckIP(object):

    def __init__(self, judgeScore=60, sourceScore=20, baba_url="http://httpbin.org/ip", check_list=["http://www.eastmoney.com/", "http://www.10jqka.com.cn/", "https://weibo.com/", "https://www.zhihu.com/"], **kwargs):
        """
        :param judgeScore: 判断是否储存的分数
        :param sourceScore: 基础分
        :param baba_url: 爸爸url具有一票否决权,默认为校验ip网址-->"http://httpbin.org/ip"
        :param check_list: 用来检验ip的网址['https://www.baidu.com', '...']
        :param kwargs: table 存储IP的表名字,用来生成sql语句(多线程校验)
                    　　zd_ip 存储ip的字段名字,用来生成sql语句(多线程校验)
                    　　zd_port 存储port的字段名字,用来生成sql语句(多线程校验)
                    　　zd_type 存储类型 (http | https)的字段名字,用来生成sql语句(多线程校验)
                    　　zd_nmd 存储匿名度的字段名字,用来生成sql语句(多线程校验)
                    　　zd_score 存储ip得分的字段名字,用来生成sql语句(多线程校验)
        """
        self.sourceScore = sourceScore
        self.judgeScore = judgeScore
        self.baba_url = baba_url
        self.ua = UA()  # 工具类随机请求头
        self.cm = ConnMysql()  # 工具类连接MySQL数据库
        self.bf = BloomFilter(key='IPFilter')
        self.check_list = check_list
        self.HEADERS = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.q = Queue()  # 为了多线程使用校验,将列表转化为队列.
        self.q_recheck = Queue()  # 用于复检IP
        # =============多线程存储表更改表名,字段名参数部分================
        self.table = kwargs["table"] if kwargs.get("table") else "ipipip"
        self.zd_ip = kwargs["zd_ip"] if kwargs.get("zd_ip") else 'ip'
        self.zd_port = kwargs["zd_port"] if kwargs.get("zd_port") else 'port'
        self.zd_type = kwargs["zd_type"] if kwargs.get("zd_type") else 'type'
        self.zd_nmd = kwargs["zd_nmd"] if kwargs.get("zd_nmd") else 'nmd'
        self.zd_score = kwargs["zd_score"] if kwargs.get("zd_score") else 'score'

    def __send_check(self, proxies):
        """
        发送请求,来检验ip并且为ip打分
        :param proxies: 代理ip 形式为--> {"http": "http://120.77.173.13:80"}
        :return: 可否存储,透明度,得分 | True, transparent, score | False, "舍弃", 0
        """
        score = self.sourceScore
        headers = {"User-Agent": self.ua.pc_ua()}
        try:
            resp = requests.get(self.baba_url, headers=headers, proxies=proxies, timeout=3)
            assert resp.status_code == 200
        except Exception:
            return False, "舍弃", 0  # 爸爸地址执行一票否决权
        else:
            if self.baba_url == "http://httpbin.org/ip":
                try:
                    # 根据`爸爸网站` 返回的 `origin`判断是否为高匿名的ip
                    if re.search(r'://(.*?):', str(proxies)).group(1) == json.loads(resp.content.decode())["origin"]:
                        transparent = "High Anonymity"
                    else:
                        transparent = "General"
                except Exception:
                    transparent = "Unknown"
            else:
                transparent = "Unknown"
        # ====================↓自定义打分阶段↓=====================
        for check in self.check_list:
            try:
                resp = requests.get(check, headers=headers, proxies=proxies, timeout=3)
                assert resp.status_code == 200
            except Exception:
                pass
            else:
                score += 20
        # print("IP--->{}得分为{}.".format(proxies, score))
        if score >= self.judgeScore:
            return True, transparent, score  # 返回此True即此ip检验合格,可以进行储存.
        else:
            return False, "舍弃", 0

    def __mk_many_thread(self, func, q_join, t_num=3, new=False, **kwargs):
        """
        创建多个线程
        :param func: 多线程执行的函数
        :param q_join: 需要等待的队列名字
        :param t_num: 创建线程的数量
        :return:
        """
        t_list = list()  # 线程列表
        for _ in range(t_num):
            t = Thread(target=func, args=(new, kwargs,))
            t.daemon = True
            t_list.append(t)
        for xc in t_list:  # 从线程列表遍历线程.
            xc.start()
        q_join.join()
        self.cm.close()  # 关闭数据库连接

    def __put_q_recheck(self):
        """
        用于代理池复检的时候提供队列
        :return:
        """
        select_sql = """SELECT {}, {}, {} FROM {};""".format(self.zd_type, self.zd_ip, self.zd_port, self.table)
        ret_num = self.cm.cursor.execute(select_sql)
        for _ in range(ret_num):
            lx, ip, port = self.cm.cursor.fetchone()
            proxies = self.mk_proxies(lx, ip, port)  # 将查询出来的散装元素,组装成字典.
            self.q_recheck.put(proxies)  # 放入队列中去

    def __recheck(self, new=False, **kwargs):
        """
        IP复检校验函数.
        :return:
        """
        table = kwargs["table"] if kwargs.get("table") else self.table
        zd_ip = kwargs["zd_ip"] if kwargs.get("zd_ip") else self.zd_ip
        zd_port = kwargs["zd_port"] if kwargs.get("zd_port") else self.zd_port
        zd_type = kwargs["zd_type"] if kwargs.get("zd_type") else self.zd_type
        zd_nmd = kwargs["zd_nmd"] if kwargs.get("zd_nmd") else self.zd_nmd
        zd_score = kwargs["zd_score"] if kwargs.get("zd_score") else self.zd_score
        sql_list = list()  # 待删除的IP的sql语句列表
        while True:
            if not self.q_recheck.empty():
                proxies = self.q_recheck.get()
                sfbc, transparent, score = self.__send_check(proxies)  # sfbc是否保存, transparent透明度, score代理得分.
                if sfbc and new:
                    lx, ip, port = self.sp_proxies(proxies)
                    sql = """INSERT INTO {} ({}, {}, {}, {}, {}) VALUES ('{}','{}','{}','{}','{}');""".format(table, zd_type, zd_ip, zd_port, zd_nmd, zd_score, lx, ip, port, transparent, score)
                    sql_list.append(sql)
                elif sfbc is False and new is False:
                    lx, ip, port = self.sp_proxies(proxies)
                    delete_sql = """DELETE FROM `{}` WHERE `{}`='{}';""".format(self.table, self.zd_ip, ip)
                    sql_list.append(delete_sql)  # 暂存起来,避免多次操作数据库.
                else:
                    pass
                    # else第一点为sfbc=False, new=True不保存,操作新表,故直接跳过
                    # else第二点为sfbc=True, new=False保存,不操作新表,原表有,故直接跳过
                self.q_recheck.task_done()
            else:
                break
        for sql in sql_list:
            self.cm.exe(sql)

    def __mc(self):
        """
        用于多线程校验ip时使用的中间函数.
        :return:
        """
        while True:
            if not self.q.empty():
                proxies = self.q.get()
                sfbc, transparent, score = self.check_ip_single(proxies)  # sfbc是否保存, transparent透明度, score代理得分.
                if sfbc:
                    lx, ip, port = self.sp_proxies(proxies)
                    sql = """INSERT INTO {} ({}, {}, {}, {}, {}) VALUES ('{}','{}','{}','{}','{}');""".format(self.table, self.zd_type, self.zd_ip, self.zd_port, self.zd_nmd, self.zd_score, lx, ip, port, transparent, score)
                    # print(sql)
                    self.cm.exe(sql)
                self.q.task_done()
            else:
                break

    def mk_proxies(self, lx, ip, port):
        """
        将类型, ip, 端口,转换为字典格式的代理ip供requests使用
        :param lx:　类型--> http 或 https
        :param ip:　x.x.x.x
        :param port: 0~65535     2^16-1=65535个
        :return: {"http": "http://120.77.173.13:80"}
        """
        return {"{}".format(lx): "{}://{}:{}".format(lx, ip, port)}

    def sp_proxies(self, proxies):
        """
        切割字典类型ip还原成, 类型, ip, 端口
        :param proxies: {"http": "http://120.77.173.13:80"}
        :return: lx, ip, port | http, 120.77.173.13, 80
        """
        try:
            str_ip = proxies["http"]
        except Exception:
            str_ip = proxies["https"]
        l_ip = re.split(':', str_ip)
        lx = l_ip[0]
        ip = l_ip[1].strip("//")
        port = l_ip[2]
        return lx, ip, port

    def check_ip_single(self, proxies):
        """
        将传进来的ip先进行去重处理,然后调用请求打分机制.
        :param proxies: 形式为--> {"http": "http://120.77.173.13:80"}
        :return: 可否存储,透明度,得分 | True, transparent, score | False, "舍弃", 0
        """
        try:
            str_ip = proxies["http"]
        except Exception:
            str_ip = proxies["https"]
        if not self.bf.isContains(str_ip):  # Bloom去重判断是否存在
            # time.sleep(1)  # 每次检验一个IP睡一秒.避免多线程校验的时候干崩测试网站.
            self.bf.insert(str_ip)
            return self.__send_check(proxies)  # 调用请求打分机制.
        else:
            return False, "已存在", "分数及格"

    def check_ip_many_thread(self, proxies_list, t_num=3):
        """
        多线程校验IP函数
        :param proxies_list: 带校验的IP列表
        :param t_num: 创建线程的数量
        :return:
        """
        for proxies in proxies_list:
            self.q.put(proxies)
        self.__mk_many_thread(func=self.__mc, q_join=self.q, t_num=t_num)

    def recheck_single(self, new=False, **kwargs):
        """
        (单线程)从数据库中查询出来ip进行二次校验.不合格的就删掉.
        :return:
        """
        self.__put_q_recheck()  # 调用放入队列的方法,将从数据库中查询出来的ip放入队列
        self.__recheck(new, **kwargs)

    def recheck_many_thread(self, new=False, t_num=3, **kwargs):
        """
        (多线程)从数据库中查询出来ip进行二次校验.不合格的就删掉.
        :param new: 是否使用新表new=False或new=True
        :param t_num: 线程数量, 默认为3
        :param kwargs: table 新表IP的表名字,用来生成sql语句(多线程校验)
            　　        zd_ip 新表ip的字段名字,用来生成sql语句(多线程校验)
            　　        zd_port 新表port的字段名字,用来生成sql语句(多线程校验)
            　　        zd_type 新表类型 (http | https)的字段名字,用来生成sql语句(多线程校验)
            　　        zd_nmd 新表匿名度的字段名字,用来生成sql语句(多线程校验)
            　　        zd_score 新表ip得分的字段名字,用来生成sql语句(多线程校验)
        :return:
        """
        self.__put_q_recheck()  # 调用放入队列的方法,将从数据库中查询出来的ip放入队列
        self.__mk_many_thread(func=self.__recheck, new=new, q_join=self.q_recheck, t_num=t_num, kwargs=kwargs)

# TODO:使用方法-->check_ip_single() 直接传入字典类型代理即可：-->eg: check_ip_single({"http": "http://120.77.173.13:80"})
# TODO:使用方法-->check_ip_many_thread(), 传入待校验的代理列表[{},{}],线程数量t_num, 如需要使用新表保存,需要在创建对象时候传入kwargs的多个参数.
# TODO:使用方法-->recheck_single(new=False, **kwargs), 传入是否使用新表,如果是需要传入kwargs相关参数,或创建对象时候直接传入kwargs的多个参数.
# TODO:使用方法-->recheck_many_thread(new=False, t_num=3, **kwargs), 传入是否使用新表,线程数,如果是需要传入kwargs相关参数,或创建对象时候直接传入kwargs的多个参数.

"""
1.拿到IP
2.使用redis + bloom 进行过滤
2.5---> 新增功能, 使用此代理访问它爸爸的网站http://httpbin.org/ip,如果三秒超时,此代理直接舍弃.他爸爸具有最终解释权(即代理校验网址访问不成功,一票否决).
3.将过滤后的内容进行访问测试,根据ip访问网站的个数来给IP打分(打分机制比如访问4个网站,时间都不超过3秒的,即为100分,有一个网站不合格的扣掉10分).
4.将访问测试及格的IP存储至mysql中,进行保存.

# 复检机制
1.从数据库查询出数据
2.发送请求进行校验
3.将校验不合格的删掉
"""
