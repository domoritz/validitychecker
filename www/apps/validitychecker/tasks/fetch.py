#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from celery.task import task, subtask
from celery import registry

from www.apps.validitychecker.models import Query, Article, Author, KeyValue

from www.apps.validitychecker.utils.wokmws import WokmwsSoapClient
from datetime import date, datetime

@task(ignore_result=True, name='scrape')
def fetch_soap(query="solar flares", number = 10, qobj=None):

    logger = fetch_soap.get_logger()
    logger.info("Start fetching from soap")

    query = urllib.unquote_plus(query)
    q_query = urllib.quote_plus(query)

    if qobj:
        qobj.status = Query.QUEUED
        qobj.save()

    # build query accoding to wokws api
    query = 'TS='+query

    # get session id from db
    # not getting a new sid for each query avoids throttling
    sobj, created = KeyValue.objects.get_or_create(key='SID')

    # lazy invalid function, invalid if older than 30 minutes
    valid = lambda: (datetime.now() - sobj.created_at).seconds/60 < 30

    if not created and valid():
        # get latest session id, avoid problems when no id is defined
        sessionid = sobj.value

        # initialize client with SID!
        soap = WokmwsSoapClient(sessionid)
        logger.warning("SID from db: %s" % sessionid)
    else:
        # without SID/ new sid
        soap = WokmwsSoapClient()

        # create new sid object
        sobj.value = soap.SID
        sobj.save()

        logger.warning("New authentication. Got SID: %s" % soap.SID)

    # search_soap -> extract_data -> store_in_db
    search_soap.delay(soap, qobj, query, number, callback=subtask(extract_data,
                                callback=subtask(store_in_db)))

@task(ignore_result=True)
def search_soap(soap, qobj, query, number, callback=None):

    logger = search_soap.get_logger()
    logger.info("query: %s" % query)

    # start searching
    result = soap.search(query, number)

    if callback:
        # The callback may have been serialized with JSON,
        # so best practice is to convert the subtask dict back
        # into a subtask object.
        subtask(callback).delay(qobj, result)

@task(ignore_result=True)
def extract_data(qobj, result, callback=None):
    if not hasattr(result, 'records'):
        print "Nothing found"
        return
    else:
        print "Found:", result.recordsFound

    records = []
    for record in result.records:

        record = {}
        record['title'] = record.title[0][1][0]
        #record['url'] =
        #record['snippet'] =
        #record['source'] =
        record['authors'] = record.authors[0][1]
        record['publish_date'] = date(int([x for x in record.source if x[0]=='Published.BiblioYear'][0][1][0]), 1, 1)

        records.append(record)

    if callback:
        subtask(callback).delay(qobj, records)

@task(ignore_result=True)
def store_in_db(qobj, records):
    for record in records:
        # add article
        article, _ = Article.objects.get_or_create(title=record['title'], defaults={'title': record['title'], 'publish_date': record['publish_date']})
        article.is_credible = True # set credible because it's in the isi index
        if article.status in [ Article.UNKNOWN ]:
            # fetch isi cited data
            pass
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

    if qobj:
        qobj.status = Query.FINISHED
        qobj.save()

if __name__ == '__main__':
    fetch()

