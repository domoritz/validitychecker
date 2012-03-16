#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
will crawl a website in order to get data about articles and authors


the crawler will save the data to the database
"""

from celery.task import Task
from celery.registry import tasks

from scrapy.conf import settings
from scrapy import project, signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess, Crawler

import os, urllib

from www.apps.validitychecker.models import Query
from www.apps.scrapers.scrapers.spiders import ScholarSpider, CiteseerXSpider

os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'www.apps.scrapers.scrapers.settings')

class CrawlTask(Task):

    def __init__(self):
        self.count = 0
        self.qobj = None

    def catch_item(self, sender, item, **kwargs):
        self.count += 1
        print "Got:", self.count, item

    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        self.qobj = qobj
        self.count = 0

        query = urllib.unquote_plus(query)

        logger = self.get_logger(**kwargs)
        logger.info("Query: %s" % query)

        self.qobj.status = Query.QUEUED
        self.qobj.save()


        mySettings = {'LOG_ENABLED': True, 'ITEM_PIPELINES': 'www.apps.scrapers.scrapers.pipelines.DjangoArticlePipeline'} # global settings http://doc.scrapy.org/topics/settings.html

        settings.overrides.update(mySettings)

        dispatcher.connect(self.catch_item, signal=signals.item_passed)

        # set up crawler
        crawler = Crawler(settings)

        if not hasattr(project, 'crawler'):
            crawler.install()
        crawler.configure()

        # schedule spider
        spider = self.spiderclass(query=query, number=number, qobj=qobj)
        crawler.crawl(spider)
        # crawler.engine.open_spider

        # start engine scrapy/twisted
        print "STARTING ENGINE"
        crawler.start()
        print "ENGINE STOPPED"
        crawler.stop()
        print "Fetched %s articles(s)" % self.count

    def on_success(self, retval, task_id, args, kwargs):
        self.qobj.status = Query.FINISHED
        self.qobj.message = ""
        self.qobj.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.qobj.status = Query.ERROR
        self.qobj.message = einfo
        self.qobj.save()

class CrawlScholarTask(CrawlTask):
    def __init__(self):
        CrawlTask.__init__(self)
        self.spiderclass = ScholarSpider

class CrawlCiteseerXTask(CrawlTask):
    def __init__(self):
        CrawlTask.__init__(self)
        self.spiderclass = CiteseerXSpider

tasks.register(CrawlScholarTask)

