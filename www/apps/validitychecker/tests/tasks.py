#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery tasks, the task pipeline is tested in pipeline.py

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok, NG

from www.apps.validitychecker.tasks import scrape
from www.apps.validitychecker.tasks import fetch
from www.apps.validitychecker.models import Query, Article, Author

import os
from datetime import date
from www.apps.validitychecker.utils.wokmws import WokmwsSoapClient

###########################################
# Scrape Tests
###########################################


class FetchContentTest(TestCase):
    def setUp(self):
        """
        Tests that fetch_page returns something
        """

        url = 'http://scholar.google.com/scholar?as_sdt=1&num=10&q=solar+flare'
        qobj = None

        self.result = scrape.fetch_page(url, qobj)

    @test("fetch should be successful")
    def _(self):
        ok (self.result).is_a(str)
        ok (len(self.result)) > 10

class ParseTest(TestCase):
    """
    tests the scholar parser
    """
    def setUp(self):
        f = open(os.path.dirname(os.path.realpath(__file__))+'/data/scholar_solar_flare.html', 'r')

        url = 'http://scholar.google.com/scholar?as_sdt=1&num=10&q=solar+flare'
        page = f.read()
        qobj = None

        self.records = scrape.parse_scholar_page(url, page, qobj)

    @test("parsing should return 10 items")
    def _(self):
        ok (self.records).is_a(list).length(10)

    @test("records should be dict with entries")
    def _(self):
        for record in self.records:
            ok (record).contains('title')
            ok (record).contains('snippet')
            ok (record).contains('publish_date')
            ok (record).contains('source')
            ok (record).contains('authors')

    @test("entries should be parsed correctly")
    def _(self):
        for record in self.records:
            ok (len(record['title'])) > 0
            ok (len(record['snippet'])) > 0
            ok (len(record['source'])) > 0
            ok (len(record['authors'])) > 0
            ok (record['publish_date']).is_a(date)

class WriteScrapedToDBTest(TestCase):
    def setUp(self):
        qobj = Query.objects.create(query='solar flare', status=Query.RUNNING)

        records = [{'title': u'The solar flare myth', \
                'url': u'http://www.agu.org/pubs/crossref/1993/93JA01896.shtml', \
                'snippet': u'Many years of re ... !@#$%^&*() äüöƒß solar flares. This result has led to a  ...', \
                'source': u'Journal of Geophysical Research', \
                'publish_date': date(1993, 1, 1), \
                'authors': [u'JT Gosling', u'J Doe']}]
        scrape.store_in_db('solar flare', records, qobj)

        self.article = Article.objects.get(title='The solar flare myth')

    @test("title should be right")
    def _(self):
        ok(self.article.title) == 'The solar flare myth'
        ok(self.article.title) != 'the solar flare myth'

    @test("url and snippets should be right")
    def _(self):
        ok(self.article.url) == 'http://www.agu.org/pubs/crossref/1993/93JA01896.shtml'
        ok(self.article.snippet) == u'Many years of re ... !@#$%^&*() äüöƒß solar flares. This result has led to a  ...'

    @test("source should not be defined because scholar is not credible")
    def _(self):
        ok(self.article.source) != 'Journal of Geophysical Research'

    @test("publish date should be date and right")
    def _(self):
        ok(self.article.publish_date) == date(1993, 1, 1)

    @test("article should not be credible")
    def _(self):
        ok(self.article.is_credible) != True

    @test("J Doe should be an author")
    def _(self):
        _, created = Author.objects.get_or_create(name='J Doe')
        ok(created) != True

    @test("J Doe should have the article as one of his articles")
    def _(self):
        author = Author.objects.get(name='J Doe')
        ok(author.articles.all()).contains(self.article)


###########################################
# Fetch/SOAP Tests
###########################################


class SoapSetupTest(TestCase):
    def setUp(self):
        self.soap = WokmwsSoapClient()

    @test("client must have sid")
    def _(self):
        ok (self.soap).has_attr('SID')

class SoapSearchTest(TestCase):
    @classmethod
    def setUpClass(cls):
        soap = WokmwsSoapClient()
        cls.result = fetch.search_soap(soap, None, 'solar flare', 5)

    def setUp(self):
        self.result = self.__class__.result

    @test("search must return 5 results")
    def _(self):
        ok (len(self.result.records)) == 5

    @test("records should have a title")
    def _(self):
        for record in self.result.records:
            ok (record.title[0][1][0]).is_a(unicode)

    @test("search must return number of found records")
    def _(self):
        ok (self.result.recordsFound) > 0

    @test("search must return number of searched records")
    def _(self):
        ok (self.result.recordsSearched) > 0

class SoapExtractionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        soap = WokmwsSoapClient()
        result = fetch.search_soap(soap, None, 'solar flare', 5)
        cls.records = fetch.extract_data(None, result)

    def setUp(self):
        self.records = self.__class__.records

    @test("extraction has to be a list")
    def _(self):
        ok(self.records).is_a(list)

    @test("records should be dict with entries")
    def _(self):
        for record in self.records:
            ok (record).contains('title')
            ok (record).contains('publish_date')
            ok (record).contains('authors')

    @test("entries should be parsed correctly")
    def _(self):
        for record in self.records:
            ok (len(record['title'])) > 0
            ok (len(record['authors'])) > 0
            ok (record['publish_date']).is_a(date)




