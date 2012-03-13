#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from celery.task import Task
from celery.registry import tasks

from www.apps.validitychecker.models import Query, Article, Author, SID
from www.apps.scrapers.utils.wokmws import WokmwsSoapClient

from datetime import date, datetime

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
    def run(self, query="solar flares", number = 10, qobj=None, **kwargs):
        """
        Fetch from web of knowledge web services
        """
        self.qobj = qobj

        logger = self.get_logger(**kwargs)
        logger.info("Query: %s" % query)

        self.qobj.status = Query.QUEUED
        self.qobj.save()

        # build query accoding to wokws api
        query = 'TS='+query

        # get session id from db
        # not getting a new sid for each query avoids throttling
        sessionid = SID.objects.order_by('-created_at')

        # lazy invalid function, invalid if older than 30 minutes
        valid = lambda: (datetime.now() - sessionid[0].created_at).seconds/60 < 30

        if sessionid and valid():
            # get latest session id, avoid problems when no id is defined
            sessionid = sessionid[0].sid

            # initialize client with SID!
            soap = WokmwsSoapClient(sessionid)
            logger.warning("SID from db: %s" % sessionid)
        else:
            # without SID/ new sid
            soap = WokmwsSoapClient()

            # create new sid object
            s = SID(sid = soap.SID)
            s.save()

            logger.warning("new authentication \n got SID: %s" % soap.SID)

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
                author, _ = Author.objects.get_or_create(name=name)
                author.articles.add(article)
                author.save()

            # add article to query
            qobj.articles.add(article)
            qobj.save()

        print result.recordsFound

tasks.register(FetchWokmwsTask)

