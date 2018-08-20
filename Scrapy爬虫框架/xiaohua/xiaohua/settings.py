# -*- coding: utf-8 -*-

# Scrapy settings for xiaohua project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'xiaohua'

SPIDER_MODULES = ['xiaohua.spiders']
NEWSPIDER_MODULE = 'xiaohua.spiders'

# 设置处理返回数据的类及执行优先级
ITEM_PIPELINES = {'xiaohua.pipelines.XiaohuaPipeline': 100,
                  'xiaohua.pipelines.saveMysql': 200}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
