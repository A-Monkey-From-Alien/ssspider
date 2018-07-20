from pymongo import MongoClient

"""
时间:2018年7月2日
作者:alien
版本:Python3 + pymongo
说明:MongoDB数据库连接示例
"""


class ConnMongo(object):

    def __init__(self):
        # 实例化MongoClient
        self.client = MongoClient(host="127.0.0.1", port=27017)
        # 选择数据库和集合
        self.collection = self.client["mymongo"]["coll"]

    def add(self):
        """增"""
        # 插入一条
        ret = self.collection.insert_one({"name": "jack", "age": 10})
        print(ret)  # 打印结果---->   <pymongo.results.InsertOneResult object at 0x7f7090f9c888>
        print(ret.inserted_id)  # 插入数据的id  # 打印结果---->   5aa672371d41c80ebf9e9b14
        print(dir(ret))    # 打印结果---->  ['_InsertOneResult__acknowledged', '_InsertOneResult__inserted_id', '_WriteResult__acknowledged', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_raise_if_unacknowledged', 'acknowledged', 'inserted_id']

    def add_many(self):
        """插入多条"""
        ret = self.collection.insert_many([{"name": "frank"}, {"name": "bob"}])
        print("插入多条成功", ret)

    def delete(self):
        """删除"""
        ret = self.collection.delete_one({"name": "jack"})
        print(ret, "删除一条成功")
        ret = self.collection.delete_many({"name": "jack"})
        print(ret, "删除多条成功")  # 条件中的都会被删除，一条不剩．

    def change(self):
        """改"""
        ret = self.collection.update_one({"name": "frank"}, {"$set": {"name": "bob"}})
        print("更改一条数据成功", ret)
        ret = self.collection.update_many({"name": "bob"}, {"$set": {"name": "frank"}})  #
        print("更改多条数据成功", ret)

    def select(self):
        """查询"""
        ret = self.collection.find_one({"name": "frank"})
        print("查询一条数据" + "\n", ret)
        print("-" * 100)
        ret = self.collection.find({"name": "frank"})
        print("查询多条数据" + "\n", ret)
        for i in ret:
            print(i)
        print("-" * 100)
        for j in ret:
            print("在第二次遍历中！")  # 查询所返回的对象为指针(cursor)类型只能遍历一次
            print(j)
        print("-" * 100)
        ret = list(ret)  # 强行转换成列表--> 转化前应该把遍历注释掉
        print(ret)

    def finaly(self):
        self.client.close()