from redis import StrictRedis

"""
时间:2018年7月2日
作者:alien
版本:Python3 + pymysql
说明:MySQL连接示例
"""


class ConnRedis(object):

    def __init__(self):
        try:
            self.r_conn = StrictRedis(host='192.168.1.58', port=6379, db=6)  # 1.创建redis的连接
            # 注:远程连接redis需要更改redis.conf以下几点
            # 1.将bind 127.0.0.1 注释掉　或者　改为　bind 0.0.0.0
            # 2.将protect-mode 改为no
            # 3.防火墙的问题
        except Exception as e:
            print("抛出异常为:".format(e))
        else:
            result = self.r_conn.keys()  # 2.连接执行对应的操作数据库的方法.--->参考网址为http://doc.redisfans.com/
            print(result)  # [b'tsh_bj_time']  # 3.返回执行后的结果,注意:此处为二进制,需要解码~
        finally:
            pass


if __name__ == '__main__':
    rc = ConnRedis()