#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from django.db import transaction

from celery.result import BaseAsyncResult, AsyncResult, EagerResult
from celery.task import task, subtask
from celery.task.sets import TaskSet

from www.apps.validitychecker.models import Query, Article, Author, KeyValue

from www.apps.validitychecker.tasks.scrape import make_scholar_urls, fetch_page, parse_scholar_page, store_in_db
from www.apps.validitychecker.tasks.fetch import prepare_client, search_soap, extract_data, store_credible_in_db

#@transaction.commit_on_success
@task(time_limit=30, name="combined.combined_data_retrieve")
def combined_data_retrieve(query="solar flares", number = 10, qobj=None):

    logger = combined_data_retrieve.get_logger()
    logger.info("Start retrieving data")

    if not qobj:
        qobj, created = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})
        qobj.save()
        logger.warning("qobj was none")

    scholarurls = make_scholar_urls(qobj=qobj, number=number)

    #########
    # non blocking
    #########

    # run scholar fetching and parsing
    fetch_and_parse_scholar_job = [fetch_page.delay(url, qobj, callback=parse_scholar_page) for url in scholarurls]

    # fetching soap job
    # prepare_client -> search_soap -> extract_data -> store_credible_in_db
    wokws_data_result = prepare_client.delay(number=number, qobj=qobj, \
            callback=subtask(search_soap, \
            callback=subtask(extract_data, \
            callback=subtask(store_credible_in_db))))

    logger.info("submitted all jobs")

    #########
    # blocking
    #########

    # use this pattern: http://stackoverflow.com/questions/3901101/pythoncelery-chaining-jobs
    # it will return the subtask instead of data
    # the last subtask in a row will return the actual data
    #
    # while isinstance(result, Result): # while result is not the last, do a step
    #    result = result.get()

    scholarResults = []
    # wait for fetching and parsing of scholar
    for result in fetch_and_parse_scholar_job:
        while isinstance(result, EagerResult) or isinstance(result, AsyncResult): # while result is not the last, do a step
            result = result.get()
        scholarResults.append(result)


    # blocks until results are in db
    result = wokws_data_result
    while isinstance(result, EagerResult) or isinstance(result, AsyncResult):
        result = result.get()
    wpk_records = wokws_data_result

    # wokws results are already saved

    logger.info("jobs returned results")

    # let's save the results from scholar to the db
    db_job = TaskSet(tasks=[store_in_db.subtask((url, records, qobj)) for (url, records) in scholarResults])
    scholar_db_result = db_job.apply_async()

    scholar_records = scholar_db_result.join()

    logger.info("everything saved")

    ret = wpk_records, scholar_records

    return ret
