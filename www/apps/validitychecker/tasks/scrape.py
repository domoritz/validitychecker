#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import transaction

from celery.task import task, subtask
from celery import registry

from www.apps.validitychecker.models import Query, Article, Author

from lxml import etree
import re, urllib2, urllib
from StringIO import StringIO
from datetime import date

@task(ignore_result=True, name='scrape google scholar')
def scrape_scolar(query="solar flares", number = 10, qobj=None):

    logger = scrape_scolar.get_logger()
    logger.info("Start scraping")

    uq_query = urllib.unquote_plus(query)
    query = urllib.quote_plus(query)

    if qobj:
        qobj.status = Query.QUEUED
        qobj.save()

    # TODO use celery states, not query model
    #update_state(state="QUEUED", meta={})

    urls = [
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&q='+query,
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&start='+str(number)+'&q='+query,
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&start='+str(2*number)+'&q='+query
            ]

    for url in urls[:1]:
        # fetch_page -> parse_page -> store_in_db
        fetch_page.delay(url, qobj, callback=subtask(parse_scholar_page,
                                callback=subtask(store_in_db)))

@task(ignore_result=True, name='fetch content with urllib2')
def fetch_page(url, qobj, callback=None):

    logger = fetch_page.get_logger()
    logger.info("URL: %s" % url)

    headers = { 'User-Agent' : 'Mozilla/5.0' }
    req = urllib2.Request(url=url, headers=headers)
    response = urllib2.urlopen(req)
    page = response.read()

    if callback:
        # The callback may have been serialized with JSON,
        # so best practice is to convert the subtask dict back
        # into a subtask object.
        subtask(callback).delay(url, page, qobj)
    else:
        return page

@task(ignore_result=True, name='parse scholar page')
def parse_scholar_page(url, page, qobj, callback=None):
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(page), parser)

    elements = tree.xpath("//body/div[@class='gs_r']")

    # to be returned
    records = []

    for element in elements:

        a_first = lambda x: x[0] if x else ''
        a_join = lambda x: ''.join(x)
        a_split = lambda x: x.split(',')

        a_date = lambda y: date(y, 1, 1)

        def a_find(string, pattern):
            match = re.search(pattern, string)
            if match:
                return match.group(1)
            else:
                return ''

        a_int = lambda i: int(i) if i else 0


        def perform(element, *functions):
            result = element
            for f in functions:
                result = f(result)
            return result

        record = {}
        record['title'] = perform(element.xpath('h3[@class="gs_rt"]/a//text()'), a_join, unicode)
        record['url'] = perform(element.xpath('h3[@class="gs_rt"]/a/@href'), a_join, unicode)
        record['snippet'] = perform(element.xpath('div[@class="gs_rs"]//text()'), a_join, unicode)
        record['source'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'-\s+(.+)[,|-]\s+\d{4}'),  unicode)
        record['authors'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\A(.+?)\s+-\s+'), unicode, a_split)
        record['publish_date'] = perform(element.xpath('div[@class="gs_a"]//text()'), a_join, lambda x: a_find(x, r'\s+(\d{4})\s+\-'),a_int ,  a_date)

        records.append(record)

    if callback:
        subtask(callback).delay(url, records, qobj)
    else:
        return records

@transaction.commit_on_success
@task(ignore_result=True, name='save scholar data to db')
def store_in_db(url, records, qobj):
    for record in records:
        # add article
        article, _ = Article.objects.get_or_create(title=record['title'], defaults={'title': record['title'], 'publish_date': record['publish_date']})
        article.url = record['url']
        article.snippet = record['snippet']
        article.save()

        # add author and article to author
        for author in record['authors']:
            name = author.strip()
            author, _ = Author.objects.get_or_create(name=name)
            author.articles.add(article)
            author.save()

        # add article to query
        qobj.articles.add(article)
        qobj.save()

    if qobj:
        #qobj.status = Query.FINISHED
        qobj.save()
