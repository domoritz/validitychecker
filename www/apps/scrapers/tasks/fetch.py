#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from celery.task import Task
from celery.registry import tasks

from www.apps.validitychecker.models import Query, Article, Author
from www.apps.scrapers.utils.wokmws import WokmwsSoapClient

from datetime import date

class FetchTask(Task):
    def __init__(self):
        self.qobj = None

    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        self.qobj.status = Query.FINISHED
        self.qobj.message = ""
        self.qobj.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.qobj.status = Query.ERROR
        self.qobj.message = einfo
        self.qobj.save()

class FetchWokmwsTask(FetchTask):
    """
    Fetch from web of knowledge web services
    """
    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        self.qobj = qobj

        logger = self.get_logger(**kwargs)
        logger.info("Query: %s" % query)

        self.qobj.status = Query.QUEUED
        self.qobj.save()


        query = 'TS='+query

        # initialize client
        soap = WokmwsSoapClient()

        # start searching
        result = soap.search(query, number)

        # process results
        for record in result.records:
            title = record.title[0][1][0]
            year = int([x for x in record.source if x[0]=='Published.BiblioYear'][0][1][0])
            authors = record.authors[0][1]

            dat = date(year, 1, 1)

            # add article
            article, _ = Article.objects.get_or_create(title__iexact=title, defaults={'title': title, 'publish_date': dat})
            article.is_credible = True # set credible because it's in the isi index
            if article.status in [ Article.UNKNOWN ]:
                # fetch isi cited data
                pass
            article.save()

            # add author and article to author
            for author in authors:
                name = ' '.join(reversed(map(unicode.strip, author.split(',')))) # convert name from Doe, J to J Doe
                author, _ = Author.objects.get_or_create(name__iexact=name)
                author.articles.add(article)
                author.save()

            # add article to query
            qobj.articles.add(article)
            qobj.save()

        print result.recordsFound

tasks.register(FetchWokmwsTask)

