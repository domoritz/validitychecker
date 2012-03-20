#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery tasks

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from django.test.client import Client
from oktest import test, ok
import oktest
oktest.DIFF = repr

import json

class StatusTest(TestCase):
    def setUp(self):
        """
        Tests that the status page works
        """

        c = Client()
        self.response = c.get('/status/solar+flare')
        self.content = self.response.content
        self.json = json.loads(self.content)

    @test("status page should be there")
    def _(self):
        ok (self.response.status_code) == 200

    @test("status should be PENDING or SUCCESS")
    def _(self):
        ok (self.json['status'] in ['PENDING', 'SUCCESS']) == True

    @test("there should be no error on the status page")
    def _(self):
        ok (self.json['status']) != 'ERROR'
        print "Status is:", self.json['status']

    @test("there should be a resulturl")
    def _(self):
        ok (self.json['resulturl']) != ''


class IndexPageTest(TestCase):
    def setUp(self):
        """
        Tests the index/start/home page
        """

        c = Client()
        self.response = c.get('/')
        self.content = self.response.content

    @test("index page should be there")
    def _(self):
        ok (self.response.status_code) == 200
