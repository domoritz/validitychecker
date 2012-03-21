#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from celery.task import task, subtask

from www.apps.validitychecker.models import Query, Article, Author, KeyValue
from www.apps.validitychecker.tasks.db import store_in_db
from www.apps.validitychecker.utils.wokmws import WokmwsSoapClient

from datetime import date, datetime
import urllib

@task(name='fetch.wok_soap_complete')
def wok_soap_complete(number = 10, qobj=None, callback=None):
    soap = prepare_client(number=number, qobj=qobj)
    res = search_soap(soap=soap, qobj=qobj, number=number)
    rec = extract_data(qobj=qobj, result=res)
    return store_in_db(records=rec, qobj=qobj, credible=True)

@task(name='fetch.prepare_client')
def prepare_client(number = 10, qobj=None, callback=None):

    logger = prepare_client.get_logger()
    logger.info("Preaparing client")

    # get session id from db
    # not getting a new sid for each query avoids throttling
    sobj, created = KeyValue.objects.get_or_create(key='SID')

    # lazy invalid function, invalid if older than 30 minutes
    valid = lambda: (datetime.now() - sobj.created_at).seconds/60 < 30

    soap = None
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
        #return callback(soap, qobj, number)
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

        # convert name from Doe, J to J Doe
        record['authors'] = map(lambda author: ' '.join(reversed(map(unicode.strip, author.split(',')))), record['authors'])

        records.append(record)

    if callback:
        return subtask(callback).delay(qobj=qobj, records=records)
    else:
        return records


