#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information
"""

from celery.task import Task
from celery.registry import tasks

from www.apps.validitychecker.models import Query
from www.apps.scrapers.utils.wokmws import WokmwsSoapClient

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
        result = soap.search(query)
        for record in result.records:
            print record.title[0][1][0]
            print record.authors[0][1]
        print result.recordsFound

tasks.register(FetchWokmwsTask)

