# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import requests
import pymysql


class XiaohuaPipeline(object):
    def process_item(self, item, spider):
        # 获取当前工作目录
        baseDir = os.getcwd()
        # 下载图片
        with open(baseDir + '\\xiaohua\\image\\' + item['name'] + '.png', 'wb') as f:
            f.write(requests.get(item['imgUrl']).content)

        return item


class saveMysql(object):
    # 获取数据库连接
    def getConn(self, host, userName, pwd, dbName, port):
        return pymysql.connect(host=host, user=userName, password=pwd, database=dbName, port=port)

    def process_item(self, item, spider):
        host = "127.0.0.1"
        port = 3306
        userName = "root"
        pwd = "123456"
        dbName = "test"
        connection = self.getConn(host, userName, pwd, dbName, port)

        name = item['name']
        imgUrl = item['imgUrl']
        print(name)
        print(imgUrl)
        try:
            with connection.cursor() as cursor:
                # 创建更新值的sql语句
                sql = """INSERT INTO XIAOHUA(username,imgurl) VALUES (%s,%s)"""
                # 执行sql语句
                # excute 的第二个参数可以将sql缺省语句补全，一般以元组的格式
                num = cursor.execute(sql, (name, imgUrl))
                print("插入执行成功条数:", num)

            # 提交本次插入的记录
            connection.commit()
        except Exception as e:
            print("发生异常，异常信息:", e)
            # 发生错误时进行回滚
            connection.rollback()
        finally:
            if connection:
                # 关闭数据库连接
                connection.close()
        return item
