import requests
import os
import pymysql
import re
import urllib.parse
from bs4 import BeautifulSoup
from utils.tools import UtilLogger


def getHtmlText(url):
    try:
        r = requests.get(url, timeout=15, stream=True)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception as e:
        print(e)
        return -1


def __init__(self):
    self.log = UtilLogger('SougouSpider',
                          os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_SougouSpider.log'))


class SougouSpider():

    def __init__(self):
        self.urlSet = set()
        self.MysqlUtil = MysqlUtil()
        self.log = UtilLogger('SougouSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_SougouSpider.log'))

    def validateTitle(self, title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        new_title = re.sub(rstr, "_", title)
        return new_title

    def getNavList(self, html, navTextList):

        res = []
        soup = BeautifulSoup(html, 'lxml')
        navList = soup.find_all('li', class_="nav_list")
        for i in range(0, len(navList)):
            url = 'https://pinyin.sogou.com' + navList[i].a['href']
            type = navTextList[i]
            res.append({'type1': type, 'url': url})
        return res

    def getCateList(self, html, type1):
        """
        解析列表页的所有分类名
        :param html: 文本
        :param type1: 一级目录名
        :return:
        """
        res = []
        soup = BeautifulSoup(html, 'lxml')
        cates = soup.find('div', {'id': 'dict_cate_show'})
        listA = cates.find_all('a')
        for li in listA:
            type2 = li.text.replace('"', '')
            url = 'https://pinyin.sogou.com' + li['href'] + '/default/{}'
            # 获取每个种类的页数
            htmlForPage = getHtmlText(url)
            soupForPage = BeautifulSoup(htmlForPage, 'lxml')
            pageAll = soupForPage.find('div', {'id': 'dict_page_list'})
            pageAList = pageAll.find_all('a')
            page = 0
            if len(pageAList) > 0:
                page = pageAList[len(pageAList) - 2].text
            res.append({'url': url, 'type1': type1, 'type2': type2, 'page': page})
        return res

    def getDownloadList(self, html, type1, type2):
        """
        解析搜狗词库的列表页面
        :param html: 文件
        :param type1: 一级目录名
        :param type2: 二级目录名
        :return: list
        每一条数据都为字典类型
        """
        res = []
        try:
            soup = BeautifulSoup(html, 'lxml')
            # 偶数部分
            divs = soup.find_all('div', class_='dict_detail_block odd')
            for data in divs:
                name = self.validateTitle(data.find('div', class_='detail_title').a.text)
                url = urllib.parse.unquote(data.find('div', class_='dict_dl_btn').a['href'])
                if url in self.urlSet:
                    continue
                contents = data.find_all('div', class_='show_content')
                wordExample = contents[0].text
                downloadNum = contents[1].text
                updateTime = contents[2].text
                item = {'fileName': name, 'wordExample': wordExample,
                        'downloadNum': downloadNum, 'updateTime': updateTime, 'type1': type1, 'type2': type2,
                        'url': url}
                res.append(item)
                self.MysqlUtil.save(item)
                self.downloadScel(url, name)
                self.urlSet.add(url)
            # 奇数部分
            divs = soup.find_all('div', class_='dict_detail_block')
            for data in divs:
                name = self.validateTitle(data.find('div', class_='detail_title').a.text)
                url = urllib.parse.unquote(data.find('div', class_='dict_dl_btn').a['href'])
                if url in self.urlSet:
                    continue
                contents = data.find_all('div', class_='show_content')
                wordExample = contents[0].text
                downloadNum = contents[1].text
                updateTime = contents[2].text
                item = {'fileName': name, 'wordExample': wordExample,
                        'downloadNum': downloadNum, 'updateTime': updateTime, 'type1': type1, 'type2': type2,
                        'url': url}
                res.append(item)
                self.MysqlUtil.save(item)
                self.downloadScel(url, name)
                self.urlSet.add(url)
        except Exception as e:
            print('解析失败 %s' % e)
            return -1
        return res

    def downloadScel(self, url, name):
        # 下载文件
        baseDir = os.getcwd()
        filename = baseDir + '\\data\\' + name + '.scel'
        with open(filename, 'wb') as f:
            f.write(requests.get(url, timeout=30, stream=True).content)
            self.log.info('{} 词库文件下载完毕'.format(name))

    def start(self):
        """
        解析搜狗词库的下载地址和分类名称
        """
        navTextList = ['城市信息', '自然科学', '社会科学', '工程应用', '农林渔畜', '医学医药',
                       '电子游戏', '艺术设计', '生活百科', '运动休闲', '人文科学', '娱乐休闲']
        html = getHtmlText('https://pinyin.sogou.com/dict/cate/index/167')
        navList = self.getNavList(html, navTextList)
        for nav in navList:
            # print(nav)
            self.log.info('正在解析页面 {}'.format(nav['url']))
            # 获取当前工作目录
            baseDir = os.getcwd()
            filename = baseDir + '\\data\\cate.txt'

            # with open(filename, 'a', encoding='utf-8') as f:
            #     f.write(str(nav) + '\n')

            html = getHtmlText(nav['url'])
            cateList = self.getCateList(html, nav['type1'])
            for cate in cateList:
                for i in range(1, int(cate['page']) + 1):
                    currUrl = cate['url'].format(i)
                    # print(currUrl)
                    self.log.info('正在解析页面 {}'.format(currUrl))
                    # with open(filename, 'a', encoding='utf-8') as f:
                    #     f.write('    ' + str(currUrl) + '\n')

                    html = getHtmlText(currUrl)
                    if html != -1:
                        downloadList = self.getDownloadList(html, nav['type1'], cate['type2'])
                        for download in downloadList:
                            # print(download)
                            self.log.info('正在解析页面 {}'.format(download['url']))
                            # with open(filename, 'a', encoding='utf-8') as f:
                            #     f.write('          ' + str(download) + '\n')


class MysqlUtil():

    # 获取数据库连接
    def getConn(self, host, userName, pwd, dbName, port):
        return pymysql.connect(host=host, user=userName, password=pwd, database=dbName, port=port)

    def save(self, item):
        # 将item里的数据拿出来
        fileName = item['fileName']
        url = item['url']
        type1 = item['type1']
        type2 = item['type2']
        wordExample = item['wordExample']
        downloadNum = item['downloadNum']
        updateTime = item['updateTime']

        host = "127.0.0.1"
        port = 3306
        userName = "root"
        pwd = "123456"
        dbName = "test"
        connection = self.getConn(host, userName, pwd, dbName, port)

        try:
            with connection.cursor() as cursor:
                # 创建更新值的sql语句
                sql = """INSERT INTO SOGOUCATE(file_name,url,word_example,download_num,update_time,type1,type2) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                # 执行sql语句
                # excute 的第二个参数可以将sql缺省语句补全，一般以元组的格式
                num = cursor.execute(sql, (fileName, url, wordExample, downloadNum, updateTime, type1, type2))
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


if __name__ == '__main__':
    SougouSpider().start()
