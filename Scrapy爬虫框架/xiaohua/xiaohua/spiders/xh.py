# -*- coding: utf-8 -*-
import scrapy
from xiaohua.items import XiaohuaItem


# class XhSpider(scrapy.Spider):
#     name = 'xh'
#     allowed_domains = ['xiaohuar.com']
#     start_urls = ['http://www.xiaohuar.com/list-1-1.html']
#
#     def parse(self, response):
#         items = []
#         picList = response.xpath('//div[@class="img"]/a')
#         for pic in picList:
#             item = XiaohuaItem()
#             item['name'] = pic.xpath('./img/@alt').extract()[0]
#             item['imgUrl'] = 'http://www.xiaohuar.com' + pic.xpath('./img/@src').extract()[0]
#             items.append(item)
#         return items
class XhSpider(scrapy.Spider):
    name = 'xh'
    allowed_domains = ['xiaohuar.com']
    start_urls = ['http://www.xiaohuar.com/hua/']

    urlSet = set()

    def parse(self, response):

        if response.url.startswith('http://www.xiaohuar.com/list-'):
            picList = response.xpath('//div[@class="img"]/a')
            for pic in picList:
                item = XiaohuaItem()
                item['name'] = pic.xpath('./img/@alt').extract()[0]
                item['imgUrl'] = 'http://www.xiaohuar.com' + pic.xpath('./img/@src').extract()[0]
                yield item

        urls = response.xpath('//a/@href').extract()
        for url in urls:
            if url.startswith("http://www.xiaohuar.com/list-"):
                if url in self.urlSet:
                    pass
                else:
                    self.urlSet.add(url)
                    yield self.make_requests_from_url(url)
            else:
                pass
