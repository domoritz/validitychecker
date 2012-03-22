#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery.task import task, subtask

from www.apps.validitychecker.models import Query, Article, Author, KeyValue
from www.apps.validitychecker.utils.perform import *
from www.apps.validitychecker.utils.isi_post import IsiFetcher

from lxml import etree
import urllib2, urllib
from StringIO import StringIO
from datetime import date, datetime

# Google Scholar

@task(name='scrape.make_scholar_urls')
def make_scholar_urls(number, qobj, callback=None):
    query = urllib.quote_plus(qobj.query)

    step = 80 # max 100
    urls = ['http://scholar.google.com/scholar?as_sdt=1&as_vis=1&num='+str(step)+'&start='+str(start)+'&q='+query for start in range(0, number, step)]

    if callback:
        return [subtask(callback).delay(url, qobj) for url in urls]
    else:
        return urls

@task(time_limit=25, name='scrape.fetch_page_from_url')
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
        record['authors'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\A(.+?)\s+-\s+'), unicode, a_split_komma, m_trim)
        record['publish_date'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\s+(\d{4})\s+\-'),a_int, a_date)

        records.append(record)

    logger = parse_wok_page.get_logger()
    logger.warning("Got %d results for the query '%s' from scholar" % (len(records), qobj.query))

    if callback:
        return subtask(callback).delay(records, qobj)
    else:
        return url, records


# Web of Knwoledge

@task(time_limit=45, name='scrape.get_wok_page', max_retries=3)
def get_wok_page(qobj, number, callback=None):
    logger = get_wok_page.get_logger()
    # get session id from db
    sobj, created = KeyValue.objects.get_or_create(key='SID_web')

    # lazy invalid function, invalid if older than 10 minutes
    valid = lambda: (datetime.now() - sobj.created_at).seconds/60 < 10

    if not created and valid():
        # get latest session id, avoid problems when no id is defined
        sessionid = sobj.value

        # initialize fetcher with SID!
        fetcher = IsiFetcher(sid=sessionid)
        logger.warning("SID for web from db: %s" % sessionid)
    else:
        # without SID/ new sid
        fetcher = IsiFetcher()

        # create new sid object
        sobj.value = fetcher.SID
        sobj.save()

        logger.warning("New SID from web. Got SID: %s" % fetcher.SID)

    query = urllib.unquote_plus(qobj.query)
    page = fetcher.fetch(query, number)

    if callback:
        return subtask(callback).delay(page, qobj)
    else:
        return page

@task(name='scrape.parse_wok_page')
def parse_wok_page(page, qobj, callback=None):
    logger = parse_wok_page.get_logger()

    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(page), parser)

    elements = tree.xpath('//td[@class="summary_data"]')

    # to be returned
    records = []
    for element in elements:
        record = {}
        record['title'] = perform(element.xpath('a/value//text()'), a_join, unicode)
        record['source'] = perform(element.xpath('span[contains(text(),"Source")]/following-sibling::text()')[0], unicode, unicode.strip)
        record['authors'] = perform(element.xpath('span[contains(text(),"Author")]/following-sibling::text()')[0], unicode, a_split_semicolon, m_trim)
        record['publish_date'] = perform(element.xpath('span[contains(text(),"Published")]/following::text()')[1], lambda x: a_find(x, r'(\d{4})'),a_int, a_date)
        record['times_cited'] = perform(element.xpath('span[contains(text(),"Times Cited")]/following::text()')[1], a_trim, lambda s: s.replace(',',''), a_int)


        # remove et al
        record['authors'] = filter(lambda author: not author.startswith('et al'), record['authors'])

        # convert name from Doe, J to J Doe
        record['authors'] = map(lambda author: ' '.join(reversed(map(unicode.strip, author.split(' ')))), record['authors'])

        records.append(record)

    logger.warning("Got %d results for the query '%s' from isi/wok" % (len(records), qobj.query))

    if callback:
        return subtask(callback).delay(records=records, qobj=qobj)
    else:
        return records

