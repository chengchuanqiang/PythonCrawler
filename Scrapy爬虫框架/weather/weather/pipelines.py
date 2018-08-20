# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import requests
import json
import pymysql
import time


class WeatherPipeline(object):
    # 时间戳
    ticks = str(round(time.time()))

    def process_item(self, item, spider):
        # 获取当前时间
        timeVal = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 获取当前工作目录
        baseDir = os.getcwd()
        filename = baseDir + '\\weather\\data\\weather' + self.ticks + '.txt'

        with open(filename, 'a', encoding='utf-8') as f:
            f.write(item['date'] + ' ')
            f.write(item['week'] + ' ')
            f.write(item['temperature'] + ' ')
            f.write(item['weather'] + ' ')
            f.write(item['wind'] + '\n')

        # 下载图片
        with open(baseDir + '\\weather\\data\\image\\' + item['date'] + '.png', 'wb') as f:
            f.write(requests.get(item['img']).content)
        return item


class W2json(object):
    # 时间戳
    ticks = str(round(time.time()))

    def process_item(self, item, spider):
        # 获取当前时间
        timeVal = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        # 获取当前工作目录
        baseDir = os.getcwd()
        filename = baseDir + '\\weather\\data\\weather' + self.ticks + '.json'

        # ensure_ascii = False 防止中文输出ASCII码
        # indent = 4 格式化json操作
        with open(filename, 'a', encoding='utf-8') as f:
            line = json.dumps(dict(item), ensure_ascii=False, indent=4) + ',\n'
            f.write(line)
        return item


class W2mysql(object):

    # 获取数据库连接
    def getConn(self, host, userName, pwd, dbName, port):
        return pymysql.connect(host=host, user=userName, password=pwd, database=dbName, port=port)

    def process_item(self, item, spider):
        # 将item里的数据拿出来
        date = item['date']
        week = item['week']
        temperature = item['temperature']
        weather = item['weather']
        wind = item['wind']
        img = item['img']

        host = "127.0.0.1"
        port = 3306
        userName = "root"
        pwd = "123456"
        dbName = "test"
        connection = self.getConn(host, userName, pwd, dbName, port)

        try:
            with connection.cursor() as cursor:
                # 创建更新值的sql语句
                sql = """INSERT INTO WEATHER(date,week,temperature,weather,wind,img) VALUES (%s,%s,%s,%s,%s,%s)"""
                # 执行sql语句
                # excute 的第二个参数可以将sql缺省语句补全，一般以元组的格式
                num = cursor.execute(sql, (date, week, temperature, weather, wind, img))
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
