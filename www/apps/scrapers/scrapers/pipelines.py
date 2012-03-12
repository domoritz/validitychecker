#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from django.db.utils import IntegrityError

from www.apps.validitychecker.models import Article, Author, Query

class DjangoArticlePipeline(object):
    def process_item(self, item, spider):
        ret = False

        qobj = spider.qobj

        if not qobj:
            # this happens if you use scrapy from the command line
            qobj, _ = Query.objects.get_or_create(query__iexact=spider.query)

        try:
            # save article
            djangoObj = item.save()

            ret = True
        except IntegrityError as e:
            # we already have the article in the database
            print e
            print item['title']
            djangoObj = Article.objects.get(title__iexact=item['title'])
            #raise DropItem(e)


        print "saving authors and query..."

        djangoObj.save()

        # add author(s)
        authors = item['author']
        for name in authors.split(','):
            name = name.strip('')
            name = name.strip(u'…')
            if name not in ['']:
                author, _ = Author.objects.get_or_create(name__iexact=name)
                author.articles.add(djangoObj)
                author.save()

        # add article to query
        qobj.articles.add(djangoObj)
        qobj.save()

        if ret:
            return item


