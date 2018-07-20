from pymysql import Connect
from threading import Lock


class ConnMysql(object):
    # ===================数据库连接===================
    def __init__(self, host='localhost', port=3306, user='root', password='mysql', database="allip", charset='utf8'):
        self.lock = Lock()
        try:
            self.conn = Connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset=charset
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print("数据库连接异常:{}".format(e))
            print("请检查您是否使用了默认的数据库参数...")
        else:
            pass
        finally:
            pass

    # ===================保存数据===================
    def exe(self, sql_language):
        try:
            # 数据库插入数据
            self.lock.acquire()  # 获取锁,多线程应用.
            self.cursor.execute(sql_language)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print("执行sql语句失败...{}".format(e))
        else:
            pass
        finally:
            self.lock.release()  # 释放锁

    def close(self):
        self.cursor.close()
        self.conn.close()

