# -*- coding: utf-8 -*-
import scrapy
from weather.items import WeatherItem


class SztianqiSpider(scrapy.Spider):
    name = 'SZtianqi'
    allowed_domains = ['www.tianqi.com']

    start_urls = []

    # 需要爬取城市的名称
    cityList = ['beijing']

    for city in cityList:
        start_urls.append('https://' + allowed_domains[0] + '/' + city)

    def parse(self, response):

        items = []
        dateAndImgList = response.xpath('//ul[@class="week"]/li')
        weatherList = response.xpath('//ul[@class="txt txt2"]/li')
        temperatureList = response.xpath('//div[@class="zxt_shuju"]/ul/li')
        windList = response.xpath('//ul[@class="txt"]/li')

        for i in range(0, len(dateAndImgList)):
            item = WeatherItem()
            item['date'] = dateAndImgList[i].xpath('./b/text()').extract()[0]
            item['week'] = dateAndImgList[i].xpath('./span/text()').extract()[0]
            item['img'] = 'https://' + self.allowed_domains[0] + dateAndImgList[i].xpath('./img/@src').extract()[0]

            item['temperature'] = temperatureList[i].xpath('./b/text()').extract()[0] + "℃ ~ " + \
                                  temperatureList[i].xpath('./span/text()').extract()[0] + "℃"

            item['weather'] = weatherList[i].xpath('./text()').extract()[0]
            item['wind'] = windList[i].xpath('./text()').extract()[0]

            items.append(item)
        return items
