# -*- coding: utf-8 -*-

###################################################################################
###################################################################################

# When running crawler, if you get "OSError: Not a gzipped file (b'\r\n')",
# add the following under "DOWNLOADER_MIDDLEWARES" in settings.py file:
# 'scrapy.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware':None,

###################################################################################
###################################################################################

import logging   # for logging
from logging.handlers import TimedRotatingFileHandler   # for logging

import scrapy
from scrapy.loader import ItemLoader   # for item loader

from re_crawler.items import ReCrawlerItem   # to load items for iteam loader

import re

# log file setting
REGULAR_LOG_FILE = "reCrawler-log.log"   # all logs will be saved to this file
crawler_logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: [%(name)-12s] %(message)s')
# crawler_logger.setLevel(logging.DEBUG)

parse_fh = TimedRotatingFileHandler(
                                    # handler for all logs, and rotated at midnight and keep upto backup logs of the past 7 days
                                    REGULAR_LOG_FILE,
                                    when='midnight',
                                    interval=1,
                                    backupCount=7
                                )

parse_fh.setFormatter(formatter)   # setting the format for file handler
parse_fh.setLevel(logging.DEBUG)   # setting the level for each handler
crawler_logger.addHandler(parse_fh)   # adding the handlers


class ReCrawler(scrapy.Spider):
    name = "recrawler"

    def start_requests(self):
        urls = [
            'http://vip.mk.co.kr/newSt/price/newsFlash.php?p_page=1&stCode=005930&sCode=21&termDatef=&search=005930&topGubun=',
            'http://vip.mk.co.kr/newSt/price/newsFlash.php?p_page=2&stCode=005930&sCode=21&termDatef=&search=005930&topGubun=',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self, response):
        pattern = "상승세 \+\d{0,2}\.\d{0,2}%"
        num = 0
        url_list = []
        base_url = "http://vip.mk.co.kr/newSt/price"
        for item in response.xpath('//td[@class="title"]/a/text()').extract():
            if re.search(pattern, item):
                url_list.append(base_url+response.xpath('//td[@class="title"]/a/@href').extract()[num][1:])
            num += 1

        for each_article in url_list:
            yield scrapy.Request(url=each_article, callback=self.parse_contents)


    def parse_contents(self, response):
        item_loader = ItemLoader(item=ReCrawlerItem(), response=response)
        item_loader.add_xpath('title', '//font[@class="headtitle"]/text()')
        item_loader.add_value('url', response.url)

        return item_loader.load_item()