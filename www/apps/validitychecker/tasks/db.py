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
@task(name='scrape.store_non_credible_in_db')
def store_non_credible_in_db(url, records, qobj):
    for record in records:
        # add article
        article, _ = Article.objects.get_or_create(title=record['title'], defaults={'title': record['title']})
        article.url = record['url']
        article.snippet = record['snippet']

        d = record['publish_date']
        if d:
            article.publish_date = d

        if article.state == Article.INCOMPLETE and article.snippet and article.url and article.publish_date:
            # set as complete if all interesting things are set
            article.state = Article.COMPLETE
        else:
            article.state = Article.INCOMPLETE

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


#@transaction.commit_on_success
@task(name='fetch.store_credible_in_db')
def store_credible_in_db(qobj, records):
    if not records:
        return []

    for record in records:
        # add article
        article, _ = Article.objects.get_or_create(title=record['title'], defaults={'title': record['title'], 'publish_date': record['publish_date']})

        article.is_credible = True # set credible because it's in the isi index

        if article.state in [ Article.INCOMPLETE ]:
            # fetch isi cited data
            pass


        if article.state == Article.INCOMPLETE and article.snippet and article.url and article.publish_date:
            # set as complete if all interesting things are set
            article.state = Article.COMPLETE
        else:
            article.state = Article.INCOMPLETE

        article.save()

        # add author and article to author
        for author in record['authors']:
            name = ' '.join(reversed(map(unicode.strip, author.split(',')))) # convert name from Doe, J to J Doe
            author, _ = Author.objects.get_or_create(name=name)
            author.articles.add(article)
            author.save()

        # add article to query
        qobj.articles.add(article)

    qobj.save()

    return records
