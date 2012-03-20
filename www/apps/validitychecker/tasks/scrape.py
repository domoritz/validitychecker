#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery.task import task, subtask

from www.apps.validitychecker.models import Query, Article, Author
from www.apps.validitychecker.utils.perform import *

from lxml import etree
import urllib2, urllib
from StringIO import StringIO

@task(name='scrape.make_scholar_urls')
def make_scholar_urls(number, qobj, callback=None):
    query = urllib.quote_plus(qobj.query)

    step = 80 # max 100
    urls = ['http://scholar.google.com/scholar?as_sdt=1&as_vis=1&num='+str(step)+'&start='+str(start)+'&q='+query for start in range(0, number, step)]

    if callback:
        return [subtask(callback).delay(url, qobj) for url in urls]
    else:
        return urls

@task(name='scrape.fetch_page_from_url')
def fetch_page_from_url(url, qobj, callback=None):

    logger = fetch_page_from_url.get_logger()
    logger.info("URL: %s" % url)

    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(req)
    page = response.read()

    if callback:
        # The callback may have been serialized with JSON,
        # so best practice is to convert the subtask dict back
        # into a subtask object.
        return subtask(callback).delay(url, page, qobj)
    else:
        return url, page

@task(name='scrape.parse_scholar_page')
def parse_scholar_page(url, page, qobj, callback=None):
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(page), parser)

    elements = tree.xpath("//body/div[@class='gs_r']")

    # to be returned
    records = []

    for element in elements:
        record = {}
        record['title'] = perform(element.xpath('h3[@class="gs_rt"]/a//text()'), a_join, unicode)
        record['url'] = perform(element.xpath('h3[@class="gs_rt"]/a/@href'), a_join, unicode)
        record['snippet'] = perform(element.xpath('div[@class="gs_rs"]//text()'), a_join, unicode)
        record['source'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'-\s+(.+)[,|-]\s+\d{4}'),  unicode)
        record['authors'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\A(.+?)\s+-\s+'), unicode, a_split, m_trim)
        record['publish_date'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\s+(\d{4})\s+\-'),a_int, a_date)

        records.append(record)

    if callback:
        return subtask(callback).delay(url, records, qobj)
    else:
        return url, records

