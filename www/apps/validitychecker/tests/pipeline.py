#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery task pipelines

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok, NG

from www.apps.validitychecker.tasks.scrape import make_scholar_urls, fetch_page, parse_scholar_page, store_in_db
from www.apps.validitychecker.tasks.fetch import prepare_client, search_soap, extract_data, store_credible_in_db
from www.apps.validitychecker.tasks import *

from celery.task import task, subtask
from www.apps.validitychecker.models import Query, Article
from celery.result import BaseAsyncResult, AsyncResult, EagerResult

class ScrapeScholarPipelineTestCase(TestCase):
    def setUp(self):
        qobj = Query(query ='ice+cream')
        qobj.save()

        number = 10
        # fetch_page -> parse_page -> store_in_db
        self.result = make_scholar_urls.delay(number, qobj, \
            callback=subtask(fetch_page, \
            callback=subtask(parse_scholar_page, \
            callback=subtask(store_in_db))))
        self.result.get() # block

        self.articles = Article.objects.all()

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

class SoapPipelineTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        qobj = Query(query ='ice+cream')
        qobj.save()

        number = 10
        result = prepare_client.delay(number, qobj, \
            callback=subtask(search_soap, \
            callback=subtask(extract_data, \
            callback=subtask(store_credible_in_db))))

        cls.result = []
        while isinstance(result, EagerResult) or isinstance(result, AsyncResult):
            result = result.get()
            cls.result.append(result)

    def setUp(self):
        self.result = self.__class__.result
        self.articles = Article.objects.all()

    @test("the whole soap pipeline should work")
    def _(self):
        for result in self.result[:-1]:
            ok (result.successful()) == True
        ok (self.result[-1]).is_a(list)

    @test("at least 5 articles for ice cream")
    def _(self):
        ok(len(self.articles)) >= 5

    @test("article should have title")
    def _(self):
        for article in self.articles:
            ok(len(article.title)) > 0

    @test("article should have credible")
    def _(self):
        for article in self.articles:
            ok(article.is_credible) == True

    @test("state should be incomplete")
    def _(self):
        for article in self.articles:
            ok(article.state) == Article.INCOMPLETE


class CompleteRetrieveTestCase(TestCase):
    def setUp(self):
        self.result = combined.combined_data_retrieve()

    @test("result should not be empty")
    def _(self):
        ok(len(self.result)) > 0


