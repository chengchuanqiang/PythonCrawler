# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import requests


class XiaohuaPipeline(object):
    def process_item(self, item, spider):
        # 获取当前工作目录
        baseDir = os.getcwd()
        # 下载图片
        with open(baseDir + '\\xiaohua\\image\\' + item['name'] + '.png', 'wb') as f:
            f.write(requests.get(item['imgUrl']).content)
        return item
