from pymysql import connect

"""
时间:2018年7月2日
作者:alien
版本:Python3 + pymysql
说明:MySQL连接示例
"""


class ConnMysql(object):

    def __init__(self):
        try:
            self.conn = connect(  # 1.创建连接
                host='rds0m2qeaoi7ver7sq74q.mysql.rds.aliyuncs.com',
                port=3306,
                user='cmsing',
                password='cmsing123test',  # 测试服务器
                database='cmsing',
                charset='utf8'
            )
            self.cursor = self.conn.cursor()  # 2.创建该连接的光标
        except Exception as e:
            print("测试服务器MySQL连接失败...{}".format(e))

    def exe_sql(self):
        """执行sql语句"""
        try:
            sql = """select count(*) from TABLE;"""
            self.cursor.execute(sql)  # 3.用光标来执行sql语句
            self.conn.commit()  # 4.用连接来`提交`或`回滚`
        except Exception as e:
            self.conn.rollback()  # 4.回滚
            print("抛出异常为:".format(e))
        else:
            pass
        finally:
            self.cursor.close()  # 5.执行完毕后关闭所创建的光标
            self.conn.close()  # 6.用完此连接最后进行关闭
