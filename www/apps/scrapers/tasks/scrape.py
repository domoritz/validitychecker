#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery.task import Task
from celery.registry import tasks

from twisted.internet import reactor

from www.apps.validitychecker.models import Query, Article, Author
from www.apps.scrapers.utils.twistedscraper import TwistedScraper

import urllib

theSemaphore = None

class ScraperTask(Task):
    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        self.qobj = qobj

        uq_query = urllib.unquote_plus(query)
        q_query = urllib.quote_plus(query)

        logger = self.get_logger(**kwargs)
        logger.info("Query: %s" % query)

        self.qobj.status = Query.QUEUED
        self.qobj.save()

        self.prepareURLs(q_query, number)

        scraper = TwistedScraper(self.urls, self.saveToDB)
        scraper.start()

        #if not reactor.running:
        #    reactor.run() # blocking


    def prepareURLs(self, query, number):
        """prepare the urls for the specific task"""
        pass

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
        # do more stuff here

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

tasks.register(ScrapeScholarTask)
