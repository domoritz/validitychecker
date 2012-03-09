#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.spider import BaseSpider
from scrapy import log
from www.apps.scrapers.scrapers.items import ArticleItem
from scrapy.contrib.loader.processor import MapCompose, TakeFirst, Join

from datetime import date

class CiteseerXSpider(BaseSpider):
    name = 'citeseerx'
    allowed_domains = ['citeseer.ist.psu.edu']

    def __init__(self, name=None, query="Solar Flares", number=10, qobj=None):
        self.query = query
        self.number = number
        self.qobj = qobj

        self.start_urls = [
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(self.number)+'&q='+query,
            #'http://scholar.google.com/scholar?as_sdt=1&num='+str(self.number)+'&start='+str(self.number)+'&q='+query
        ]

        self.intComposer = MapCompose(int)
        self.dateComposer = MapCompose(lambda d: date(d, 1, 1))
        self.cleanup = MapCompose(lambda s: s.replace('\n',''))

    def parse(self, response):
        hxs = HtmlXPathSelector(response)

        elements = hxs.select("/html/body/div[@class='gs_r']")

        log.msg("Found "+str(len(elements))+" article(s)", level=log.INFO)

        for element in elements:
            l = XPathItemLoader(item=ArticleItem(), selector=element)

            l.default_output_processor = TakeFirst()

            l.add_xpath('title', 'h3[@class="gs_rt"]/a//text()', Join(''))
            l.add_xpath('url', 'h3[@class="gs_rt"]/a/@href')
            l.add_xpath('snippet', 'div[@class="gs_rs"]//text()', Join(''), self.cleanup)
            l.add_xpath('source', 'div[@class="gs_a"]//text()', Join(''), re='-\s+(.+)[,|-]\s+\d{4}')
            l.add_xpath('publish_date', 'div[@class="gs_a"]//text()', Join(''), self.intComposer, self.dateComposer, re='\s+(\d{4})\s+\-')

            l.add_xpath('author', 'div[@class="gs_a"]//text()', TakeFirst(), re='\A(.+?)\s+-\s+')

            yield l.load_item()

