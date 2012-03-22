#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery tasks, the task pipeline is tested in pipeline.py

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok
import oktest
oktest.DIFF = repr

from www.apps.validitychecker.tasks import scrape
from www.apps.validitychecker.tasks import fetch
from www.apps.validitychecker.tasks import db
from www.apps.validitychecker.models import Query, Article, Author

import os
from datetime import date
from www.apps.validitychecker.utils.wokmws import WokmwsSoapClient

###########################################
# Scrape Tests
###########################################

# scholar
#########

class FetchScholarContentTest(TestCase):
    """
    Tests that fetch_page_from_url returns something
    """
    def setUp(self):
        url = 'http://scholar.google.com/scholar?as_sdt=1&as_vis=1&num=10&q=solar+flare'
        qobj = None

        _, self.result = scrape.fetch_page_from_url(url, qobj)

    @test("fetch should be successful")
    def _(self):
        ok (self.result).is_a(str)
        ok (len(self.result)) > 10

class ParseScholarTest(TestCase):
    """
    tests the scholar parser
    """
    def setUp(self):
        files = [open(os.path.dirname(os.path.realpath(__file__))+'/data/scholar_solar_flare.html', 'r'),
            open(os.path.dirname(os.path.realpath(__file__))+'/data/scholar_sunspots_matter.html', 'r')]

        pages = [f.read() for f in files]

        queries=['solar flare', 'do sunspots matter']
        qobjs= [Query.objects.get_or_create(query=query, defaults={'query':query})[0] for query in queries]

        self.records = [scrape.parse_scholar_page(url=None, page=pages[x], qobj=qobjs[x])[1] for x in range(2)]

    @test("parsing should return 10 items for first file")
    def _(self):
        ok (self.records[0]).is_a(list).length(10)

    @test("parsing should return 100 items for second file")
    def _(self):
        ok (self.records[1]).is_a(list).length(100)

    @test("records should be dict with entries")
    def _(self):
        for records in self.records:
            for record in records:
                ok (record).contains('title')
                ok (record).contains('snippet')
                ok (record).contains('publish_date')
                ok (record).contains('source')
                ok (record).contains('authors')

    @test("entries should be parsed correctly")
    def _(self):
        for records in self.records:
            for record in records:
                ok (len(record['title'])) > 0
                ok (len(record['snippet'])) > 0
                ok (record['source']).is_a(unicode)
                ok (len(record['authors'])) > 0
                ok (record['publish_date']).is_a(date)

class WriteScrapedToDBTest(TestCase):
    def setUp(self):
        query='solar flare'
        qobj, _ = Query.objects.get_or_create(query=query, defaults={'query':query})

        records = [{'title': u'The solar flare myth', \
                'url': u'http://www.agu.org/pubs/crossref/1993/93JA01896.shtml', \
                'snippet': u'Many years of re ... !@#$%^&*() äüöƒß solar flares. This result has led to a  ...', \
                'source': u'Journal of Geophysical Research', \
                'publish_date': date(1993, 1, 1), \
                'authors': [u'JT Gosling', u'J Doe']}]
        db.store_in_db(records=records, qobj=qobj, credible=False)

        self.article = Article.objects.get(title='The solar flare myth')

    @test("title should be right")
    def _(self):
        ok(self.article.title) == 'The solar flare myth'
        ok(self.article.title) != 'the solar flare myth'

    @test("url and snippets should be right")
    def _(self):
        ok(self.article.url) == 'http://www.agu.org/pubs/crossref/1993/93JA01896.shtml'
        ok(self.article.snippet) == u'Many years of re ... !@#$%^&*() äüöƒß solar flares. This result has led to a  ...'

    @test("publish date should be date and right")
    def _(self):
        ok(self.article.publish_date) == date(1993, 1, 1)

    @test("article should not be credible")
    def _(self):
        ok(self.article.credible) == False

    @test("J Doe should be an author")
    def _(self):
        _, created = Author.objects.get_or_create(name='J Doe')
        ok(created) == False

    @test("J Doe should have the article as one of his articles")
    def _(self):
        author = Author.objects.get(name='J Doe')
        ok(author.articles.all()).contains(self.article)

# wok
#########

class FetchWosContentTest(TestCase):
    """
    Tests that the get_wok_page task works
    """
    def setUp(self):
        query='solar flare'
        number = 10
        qobj, _ = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})
        self.page = scrape.get_wok_page(qobj, number)

    @test("wok page should not be empty")
    def _(self):
        ok (self.page).is_a(str)
        ok (len(self.page)) > 10


class ParseWokTest(TestCase):
    """
    tests the scholar parser
    """
    def setUp(self):
        files = [open(os.path.dirname(os.path.realpath(__file__))+'/data/wok_solar_flare.html', 'r'),
            open(os.path.dirname(os.path.realpath(__file__))+'/data/wok_bad_test.html', 'r')
            ]


        pages = [f.read() for f in files]

        queries=['solar flare', 'bad test']
        qobjs= [Query.objects.get_or_create(query=query, defaults={'query':query})[0] for query in queries]

        self.records = [scrape.parse_wok_page(page=page, qobj=qobj) for page, qobj in zip(pages, qobjs)]

        #from pprint import pprint
        #pprint(self.records[0])

    @test("parsing should return 100 items")
    def _(self):
        ok (self.records[0]).is_a(list).length(100)

    @test("parsing should return 81 items")
    def _(self):
        ok (self.records[1]).is_a(list).length(81)

    @test("records should be dict with entries")
    def _(self):
        for records in self.records:
            for record in records:
                ok (record).contains('title')
                ok (record).contains('publish_date')
                ok (record).contains('authors')
                ok (record).contains('source')
                ok (record).contains('times_cited')

    @test("entries should be parsed correctly")
    def _(self):
        for records in self.records:
            for record in records:
                ok (len(record['title'])) > 0
                ok (len(record['source'])) > 0
                ok (len(record['authors'])) > 0
                ok (len(record['source'])) > 0

                ok (record['times_cited']) != None
                ok (record['authors']).is_a(list)

                #print record['publish_date'], record['title']
                ok (record['publish_date']).is_a(date)

                ok (record['publish_date'].year) > 1700

###########################################
# Fetch/SOAP Tests
###########################################


class SoapSetupTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.soap = fetch.prepare_client(number = 0, qobj=None)

    def setUp(self):
        self.soap =  self.__class__.soap

    @test("client must have sid")
    def _(self):
        ok (self.soap).has_attr('SID')

    @test("second client sould have same sid")
    def _(self):
        soap = fetch.prepare_client(number = 0, qobj=None)
        ok (self.soap.SID) == soap.SID

class SoapSearchTest(TestCase):
    @classmethod
    def setUpClass(cls):
        soap = WokmwsSoapClient()
        query='solar flare'
        qobj, _ = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})
        cls.result = fetch.search_soap(soap, qobj, 5)

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
        query='climate change'
        qobj, _ = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})
        result = fetch.search_soap(soap, qobj, 5)
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




