#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the util functions/ classes

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok
import oktest
oktest.DIFF = repr

from www.apps.validitychecker.utils.isi_fetcher import IsiFetcher

class IsiFetcherTestCase(TestCase):
    """
    Tests that the IsiFetcher works
    """
    @classmethod
    def setUpClass(cls):
        cls.fetcher = IsiFetcher()

    def setUp(self):
        self.fetcher = self.__class__.fetcher
        self.sid = self.fetcher.SID

    @test("fetcher should have sid")
    def _(self):
        ok (self.sid) != None

    @test("fetch should return something")
    def _(self):
        self.page = self.fetcher.fetch('solar flare', 5)
        ok (self.page).is_a(str)

    @test("sid should not change")
    def _(self):
        self.fetcher.fetch('solar flare', 5)
        ok (self.sid) == self.fetcher.SID

