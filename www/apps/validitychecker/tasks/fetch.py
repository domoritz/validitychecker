#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from django.db import transaction

from celery.task import task, subtask

from www.apps.validitychecker.models import Query, Article, Author, KeyValue

from www.apps.validitychecker.utils.wokmws import WokmwsSoapClient
from datetime import date, datetime
import urllib

@task(name='fetch.prepare_client')
def prepare_client(number = 10, qobj=None, callback=None):

    logger = prepare_client.get_logger()
    logger.info("Preaparing client")

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

    if callback:
        return subtask(callback).delay(soap, qobj, number)
    else:
        return soap

@task(name='fetch.search_soap')
def search_soap(soap, qobj, number, callback=None):

    query = urllib.unquote_plus(qobj.query)

    # build query accoding to wokws api
    query = 'TS='+query

    logger = search_soap.get_logger()
    logger.info("query: %s" % query)

    # start searching
    result = soap.search(query, number)

    if callback:
        # The callback may have been serialized with JSON,
        # so best practice is to convert the subtask dict back
        # into a subtask object.
        return subtask(callback).delay(qobj, result)
    else:
        return result

@task(name='fetch.extract_data')
def extract_data(qobj, result, callback=None):
    logger = extract_data.get_logger()

    if not hasattr(result, 'records'):
        logger.warning("Nothing found")
        return
    else:
        logger.info("Found: %s" % result.recordsFound)

    records = []
    for wos_record in result.records:

        record = {}
        record['title'] = wos_record.title[0][1][0]
        #record['url'] =
        #record['snippet'] =
        #record['source'] =
        record['authors'] = wos_record.authors[0][1]
        record['publish_date'] = date(int([x for x in wos_record.source if x[0]=='Published.BiblioYear'][0][1][0]), 1, 1)

        records.append(record)

    if callback:
        return subtask(callback).delay(qobj, records)
    else:
        return records

#@transaction.commit_on_success
@task(name='fetch.store_credible_in_db')
def store_credible_in_db(qobj, records):
    for record in records:
        # add article
        article, _ = Article.objects.get_or_create(title=record['title'], defaults={'title': record['title'], 'publish_date': record['publish_date']})
        article.is_credible = True # set credible because it's in the isi index
        if article.state in [ Article.INCOMPLETE ]:
            # fetch isi cited data
            pass

        # article state should be incomplete if not already otherwise complete
        if article.state != Article.COMPLETE:
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
