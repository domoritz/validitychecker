#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery task pipelines

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok
import oktest
oktest.DIFF = repr

from www.apps.validitychecker.tasks.scrape import make_scholar_urls, fetch_page_from_url, parse_scholar_page
from www.apps.validitychecker.tasks.fetch import prepare_client, search_soap, extract_data, wok_soap_complete
from www.apps.validitychecker.tasks.db import store_in_db
from www.apps.validitychecker.tasks.combined import combined_data_retrieve

from celery.task import subtask
from www.apps.validitychecker.models import Query, Article
from celery.result import AsyncResult, EagerResult

###########################################
# Scraper Tests
###########################################


class ScrapeScholarPipelineTestCase(TestCase):
    def setUp(self):
        qobj = Query(query ='ice cream')
        qobj.save()

        number = 10
        # fetch_page_from_url -> parse_page -> store_in_db
        self.result = make_scholar_urls.delay(number, qobj, \
            callback=subtask(fetch_page_from_url, \
            callback=subtask(parse_scholar_page, \
            callback=subtask(store_in_db, credible=False))))
        self.result.get() # block

        self.articles = qobj.articles.all()

    @test("the whole scrape pipeline should work")
    def _(self):
        ok (self.result.successful()) == True

    @test("at least 5 articles for ice cream")
    def _(self):
        ok(len(self.articles)) >= 5

    @test("article should have title")
    def _(self):
        for article in self.articles:
            ok(len(article.title)) > 0

    @test("article should have snippet")
    def _(self):
        for article in self.articles:
            ok(len(article.snippet)) > 0

    @test("state should be incomplete")
    def _(self):
        for article in self.articles:
            ok(article.state) == Article.INCOMPLETE

    @test("state should not be credible")
    def _(self):
        for article in self.articles:
            ok(article.credible) == False

###########################################
# Fetch/SOAP Tests
###########################################

class SoapCompleteTestCase(TestCase):
    def setUp(self):
        query='ice shield'
        qobj, _ = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})
        qobj.save()

        number = 10
        self.result = wok_soap_complete.delay(number, qobj)
        self.result.get()

    @test("the complete soap should work")
    def _(self):
        ok(self.result.successful()) == True

class SoapPipelineTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        query='ice shield'
        qobj, _ = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})

        number = 10
        result = prepare_client.delay(number, qobj, \
            callback=subtask(search_soap, \
            callback=subtask(extract_data, \
            callback=subtask(store_in_db, credible=True))))

        cls.result = []
        while isinstance(result, EagerResult) or isinstance(result, AsyncResult):
            result = result.get()
            cls.result.append(result)
        cls.qobj = qobj

    def setUp(self):
        self.result = self.__class__.result
        self.articles = self.__class__.qobj.articles.all()

    @test("the whole soap pipeline should work")
    def _(self):
        for result in self.result[:-1]:
            ok(result.successful()) == True
        ok(self.result[-1]).is_a(list)

    @test("at least 5 articles for ice cream")
    def _(self):
        ok(len(self.articles)) >= 5

    @test("article should have title")
    def _(self):
        for article in self.articles:
            ok(len(article.title)) > 0

    @test("article should be credible")
    def _(self):
        for article in self.articles:
            ok(article.credible) == True

    @test("state should be incomplete because some things like the snippet are missing")
    def _(self):
        for article in self.articles:
            ok(article.state) == Article.INCOMPLETE


###########################################
# Complete test, high abstraction
###########################################

class CompleteRetrieveTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        query='sun spots'
        qobj, _ = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})
        cls.result = combined_data_retrieve.delay(query=query, number=10, qobj=qobj)
        cls.qobj = qobj

    def setUp(self):
        self.result = self.__class__.result
        self.task_id = self.result.task_id
        self.result.get() # blocking
        self.qobj = self.__class__.qobj
        self.articles = self.__class__.qobj.articles.all()
        self.qobj.task_id = self.task_id

    @test("the task id should not be the default")
    def _(self):
        ok(self.task_id) != Query.DEFAULT_ID
        ok(self.qobj.task_id) != Query.DEFAULT_ID

    @test("the complete pipeline should work")
    def _(self):
        ok (self.result.successful()) == True

    @test("all articles should have title")
    def _(self):
        for article in self.articles:
            ok(len(article.title)) > 0



