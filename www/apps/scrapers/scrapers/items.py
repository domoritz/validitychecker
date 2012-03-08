#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.contrib_exp.djangoitem import DjangoItem, Field

from www.apps.validitychecker.models import Article

class ArticleItem(DjangoItem):
    author = Field()
    django_model = Article
