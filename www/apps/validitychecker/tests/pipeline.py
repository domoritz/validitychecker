#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will test the celery task pipelines

Uses http://www.kuwata-lab.com/oktest/oktest-py_users-guide.html
"""

from django.test import TestCase
from oktest import test, ok, NG

from www.apps.validitychecker.tasks import scrape
from www.apps.validitychecker.tasks import fetch

