#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.loader import XPathItemLoader
from scrapy.spider import BaseSpider
from scrapy import log
from www.apps.scrapers.scrapers.items import ArticleItem
from scrapy.contrib.loader.processor import MapCompose, TakeFirst, Join

from datetime import date

class ScholarSpider(BaseSpider):
    name = 'scholar'
    allowed_domains = ['scholar.google.com']

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

            """
            d['footer'] = element.select("font/span[@class='gs_fl']").extract()
            d['title'] = element.select("h3[@class='gs_rt']/a/text()").extract()
            d['header'] = element.select("div[@class='gs_a']/text()")
            d['author'] = d['header']
            d['publish_date'] = date(int(d['header'].re('(\d{4})\s*\-')[0]),1,1)
            d['publication'] = d['header']
            d['ptype'] = element.select("div[@class='gs_rt']/h3/span").extract()
            d['abstract'] = element.select("div[@class='gs_rs']/text()").extract()
            d['cited_by'] = element.select("div[@class='gs_fl']/a[contains(.,'Cited by')]/text()").extract()
            d['cited_ref'] = element.select("div[@class='gs_fl']/a[contains(.,'Cited by')]").extract()
            d['from_domain'] = element.select("span[@class='gs_ggs gs_fl']/a").extract()

            item = ArticleItem()
            item['title'] = d['title']
            item['abstract'] = d['abstract']
            item['publish_date'] = d['publish_date']
            """

