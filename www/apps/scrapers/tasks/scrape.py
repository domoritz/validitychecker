#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery.task import Task
from celery.registry import tasks
from celery.task.http import HttpDispatchTask, URL

from www.apps.validitychecker.models import Query, Article, Author

from lxml import etree
import urllib, re
from StringIO import StringIO
from datetime import date


class ScraperTask(Task):
    """
    starts the httptasks
    """

    name = 'tasks.Scrape'
    max_retries = 5

    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        self.qobj = qobj

        uq_query = urllib.unquote_plus(query)
        q_query = urllib.quote_plus(query)

        logger = self.get_logger(**kwargs)
        logger.info("Query: %s" % query)

        self.qobj.status = Query.QUEUED
        self.qobj.save()

        # TODO use celery states, not query model
        self.update_state(state="QUEUED", meta={})

        self.prepareURLs(q_query, number)

        tasks = []
        for url in self.urls:
            task = HttpDispatchTask.delay(url, 'GET')
            tasks.append(task)

        for task in tasks:
            print task.get()

    def prepareURLs(self, query, number):
        """ prepare the urls for the specific task """
        pass

    def processPage(self, page):
        """ process the page and scrape data  """
        records = []
        self.saveToDB(records)

    def saveToDB(self, records):
        for record in records:
            # add article
            article, _ = Article.objects.get_or_create(title=record['title'], defaults={'title': record['title'], 'publish_date': record['publish_date']})
            article.save()

            # add author and article to author
            for author in record['authors']:
                name = author.strip()
                author, _ = Author.objects.get_or_create(name=name)
                author.articles.add(article)
                author.save()

            # add article to query
            self.qobj.articles.add(article)
            self.qobj.save()

    # celery
    def on_success(self, retval, task_id, args, kwargs):
        self.qobj.status = Query.FINISHED
        self.qobj.message = ""
        self.qobj.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.qobj.status = Query.ERROR
        self.qobj.message = einfo
        self.qobj.save()

class ScrapeScholarTask(ScraperTask):
    def prepareURLs(self, query, number):
        self.urls = [
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&q='+query,
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&start='+str(number)+'&q='+query,
            'http://scholar.google.com/scholar?as_sdt=1&num='+str(number)+'&start='+str(2*number)+'&q='+query
        ]

    def processPage(self, page):
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(page), parser)
        #result = etree.tostring(tree, pretty_print=True, method="tree")

        elements = tree.xpath("//body/div[@class='gs_r']")

        #log.msg("Found "+str(len(elements))+" article(s)", level=log.INFO)

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

        self.saveToDB(records)

tasks.register(ScrapeScholarTask)
