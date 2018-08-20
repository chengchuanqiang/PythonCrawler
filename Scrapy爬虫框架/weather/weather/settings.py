# -*- coding: utf-8 -*-

BOT_NAME = 'weather'

SPIDER_MODULES = ['weather.spiders']
NEWSPIDER_MODULE = 'weather.spiders'

ITEM_PIPELINES = {
    'weather.pipelines.WeatherPipeline': 500,
    'weather.pipelines.W2json': 500,
    'weather.pipelines.W2mysql': 500
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True
