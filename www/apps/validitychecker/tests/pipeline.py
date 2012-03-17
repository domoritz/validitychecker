#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery task pipelines

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok, NG

from www.apps.validitychecker.tasks import scrape_scolar
from www.apps.validitychecker.tasks import fetch_soap

from www.apps.validitychecker.models import Query, Article

class ScrapeScholarTestCase(TestCase):
    def setUp(self):
        qobj = Query(query ='ise+cream')
        qobj.save()

        self.result = scrape_scolar.delay('ise cream', 10, qobj)
        self.result.get() # block

        self.article = Article.objects.all()[0] # first article

    @test("the whole scrape pipeline should work")
    def _(self):
        ok (self.result.successful()) == True

    @test("article should have title")
    def _(self):
        ok(len(self.article.title)) > 0

    @test("article should have snippet")
    def _(self):
        ok(len(self.article.snippet)) > 0

    @test("state should be incomplete")
    def _(self):
        ok(self.article.state) == Article.INCOMPLETE
