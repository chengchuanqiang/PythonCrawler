import struct
import os
import time
import sys
import pymysql
from pypinyin import lazy_pinyin
from utils.tools import UtilLogger
from queue import Queue
from threading import Thread

# 建立一个线程池 用于存入解析完毕的数据
res_queue = Queue()


class ExtSougouScel():
    """
    解析搜狗词库文件
    """

    def __init__(self):
        # 拼音表偏移，
        self.startPy = 0x1540
        # 汉语词组表偏移
        self.startChinese = 0x2628
        # 全局拼音表
        self.GPy_Table = {}
        # 解析结果
        # 元组(词频,拼音,中文词组)的列表
        self.GTable = []

    def byte2str(self, data):
        """将原始字节码转为字符串"""
        i = 0
        length = len(data)
        ret = ''
        while i < length:
            x = data[i:i + 2]
            t = chr(struct.unpack('H', x)[0])
            if t == '\r':
                ret += '\n'
            elif t != ' ':
                ret += t
            i += 2
        return ret

    def getPyTable(self, data):
        """获取拼音表"""

        # if data[0:4] != "\x9D\x01\x00\x00":
        #     return None
        data = data[4:]
        pos = 0
        length = len(data)
        while pos < length:
            index = struct.unpack('H', data[pos:pos + 2])[0]
            pos += 2
            l = struct.unpack('H', data[pos:pos + 2])[0]
            pos += 2
            py = self.byte2str(data[pos:pos + l])
            self.GPy_Table[index] = py
            pos += l

    def getWordPy(self, data):
        """获取一个词组的拼音"""
        pos = 0
        length = len(data)
        ret = u''
        while pos < length:
            index = struct.unpack('H', data[pos] + data[pos + 1])[0]
            ret += self.GPy_Table[index]
            pos += 2
        return ret

    def getWord(self, data):
        """获取一个词组"""
        pos = 0
        length = len(data)
        ret = u''
        while pos < length:
            index = struct.unpack('H', data[pos] + data[pos + 1])[0]
            ret += self.GPy_Table[index]
            pos += 2
        return ret

    def getChinese(self, data):
        """读取中文表"""
        pos = 0
        length = len(data)
        while pos < length:
            # 同音词数量
            same = struct.unpack('H', data[pos:pos + 2])[0]
            # 拼音索引表长度
            pos += 2
            py_table_len = struct.unpack('H', data[pos:pos + 2])[0]
            # 拼音索引表
            pos += 2
            # 中文词组
            pos += py_table_len
            for i in range(same):
                # 中文词组长度
                c_len = struct.unpack('H', data[pos:pos + 2])[0]
                # 中文词组
                pos += 2
                word = self.byte2str(data[pos: pos + c_len])
                # 扩展数据长度
                pos += c_len
                ext_len = struct.unpack('H', data[pos:pos + 2])[0]
                # 词频
                pos += 2
                count = struct.unpack('H', data[pos:pos + 2])[0]
                # 保存
                self.GTable.append(word)
                # 到下个词的偏移位置
                pos += ext_len

    def deal(self, file_name):
        """处理文件"""
        f = open(file_name, 'rb')
        data = f.read()
        f.close()
        if data[0:12] != b'@\x15\x00\x00DCS\x01\x01\x00\x00\x00':
            print("确认你选择的是搜狗(.scel)词库? {}".format(file_name))
            sys.exit(0)
        # print("词库名：", self.byte2str(data[0x130:0x338]))
        # print("词库类型：", self.byte2str(data[0x338:0x540]))
        # print("描述信息：", self.byte2str(data[0x540:0xd40]))
        # print("词库示例：", self.byte2str(data[0xd40:self.startPy]))
        # self.getPyTable(data[self.startPy:self.startChinese])
        self.getChinese(data[self.startChinese:])
        # 返回解析完毕的所有中文词组
        return list(sorted(set(self.GTable), key=self.GTable.index))


class MysqlUtil():

    # 获取数据库连接
    def getConn(self, host, userName, pwd, dbName, port):
        return pymysql.connect(host=host, user=userName, password=pwd, database=dbName, port=port)

    def save(self, item):
        # 将item里的数据拿出来
        keyword = item['keyword']
        pinyin = item['pinyin']
        type1 = item['type1']
        type2 = item['type2']
        type3 = item['type3']

        host = "127.0.0.1"
        port = 3306
        userName = "root"
        pwd = "123456"
        dbName = "test"
        connection = self.getConn(host, userName, pwd, dbName, port)

        try:
            with connection.cursor() as cursor:
                # 创建更新值的sql语句
                sql = """INSERT INTO SOGOUKEYWORD(keyword,pinyin,type1,type2,type3) VALUES (%s,%s,%s,%s,%s)"""
                # 执行sql语句
                # excute 的第二个参数可以将sql缺省语句补全，一般以元组的格式
                num = cursor.execute(sql, (keyword, pinyin, type1, type2, type3))
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

    def selectOne(self, fileName):
        host = "127.0.0.1"
        port = 3306
        userName = "root"
        pwd = "123456"
        dbName = "test"
        connection = self.getConn(host, userName, pwd, dbName, port)
        try:
            with connection.cursor() as cursor:
                sql = """select type1,type2 from SOGOUCATE where file_name = %s"""
                cursor.execute(sql, fileName)
                res = cursor.fetchone()
                return res[0], res[1]
        except Exception as e:
            print("发生异常，异常信息:", e)
            connection.rollback()
        finally:
            if connection:
                connection.close()


def AddQueue():
    """
    遍历目录下的所有词库文件
    解析文件存入Queue
    """
    # 词库文件目录
    baseDir = os.getcwd()
    path = baseDir + '\\data\\'
    mysqlUtil = MysqlUtil()
    for filename in os.listdir(path):
        # 将关键字解析 拼成字典存入queue
        words_data = ExtSougouScel().deal(path + filename)

        # 截取文件名称
        filename = filename[0:len(filename) - 5]

        # 判断队列大小，若太大就停止从目录读文件
        s = res_queue.qsize()
        while s > 40000:
            print("sleep for a while ")
            time.sleep(20)
            s = res_queue.qsize()
            print('new size is {}'.format(s))
        for word in words_data:
            '''
            解析每一条数据，并存入队列
            '''
            keyword = word
            pinyin = " ".join(lazy_pinyin(word))

            type1, type2 = mysqlUtil.selectOne(filename)
            data = {
                'keyword': keyword,
                'pinyin': pinyin,
                'type1': type1,
                'type2': type2,
                'type3': filename,
            }
            res_queue.put_nowait(data)

            mysqlUtil.save(data)

    print('all file finshed')


def saveToDb():
    mysqlUtil = MysqlUtil()
    log = UtilLogger('crack',
                     os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_crack.log'))
    while True:
        try:
            st = time.time()
            data = res_queue.get_nowait()
            t = int(time.time() - st)
            if t > 5:
                print("res_queue", t)
            mysqlUtil.save(data)
            log.info('词库文件保存成功 {}'.format(data))
        except Exception as e:
            print("queue is empty wait for a while {}".format(e))
            time.sleep(2)


def start():
    # 使用多线程解析
    threads = list()
    # 读文件存入queue的线程
    threads.append(
        Thread(target=AddQueue))

    # 存数据库的线程
    for i in range(10):
        threads.append(
            Thread(target=saveToDb))
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    start()
