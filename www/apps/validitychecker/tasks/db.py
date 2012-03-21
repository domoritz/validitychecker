#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

#from django.db import transaction

from celery.task import task

from www.apps.validitychecker.models import Article, Author



#@transaction.commit_on_success
@task(name='scrape.store_in_db')
def store_in_db(records, qobj, credible=False):
    for record in records:
        # add article
        article, _ = Article.objects.get_or_create(title__iexact=record['title'], defaults={'title': record['title']})

        article.credible = credible

        d = record['publish_date']
        if d:
            article.publish_date = d

        if record.has_key('source'):
            article.source = record['source']

        if record.has_key('url'):
            article.url = record['url']

        if record.has_key('snippet'):
            article.snippet = record['snippet']

        article.save()

        # add author and article to author
        for name in record['authors']:
            author, _ = Author.objects.get_or_create(name=name)
            author.articles.add(article)
            author.save()

        # add article to query
        qobj.articles.add(article)

    qobj.save()

    return records
