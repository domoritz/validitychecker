#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

#from django.db import transaction

from celery.result import AsyncResult, EagerResult
from celery.task import task, subtask
from celery.task.sets import TaskSet

from www.apps.validitychecker.models import Query

from www.apps.validitychecker.tasks.scrape import make_scholar_urls, fetch_page, parse_scholar_page, store_non_credible_in_db
from www.apps.validitychecker.tasks.fetch import prepare_client, search_soap, extract_data, store_credible_in_db, wok_soap_complete

#@transaction.commit_on_success
@task(time_limit=30, name="combined.combined_data_retrieve")
def combined_data_retrieve(query=None, number=10, qobj=None):

    logger = combined_data_retrieve.get_logger()
    logger.info("Start retrieving data")

    # save task id
    qobj.task_id = combined_data_retrieve.request.id
    qobj.save()


    scholarurls = make_scholar_urls(qobj=qobj, number=number)

    #########
    # non blocking
    #########

    # run scholar fetching and parsing
    scholar_results = [
            fetch_page.delay(url, qobj,
            callback=subtask(parse_scholar_page,
            callback=subtask(store_non_credible_in_db)))
            for url in scholarurls]

    # wok api fetching
    wokws_data_result = wok_soap_complete.delay(number=number, qobj=qobj)

    logger.info("submitted all jobs")

    #########
    # blocking
    #########

    scholar_records = []
    #wait for fetching and parsing of scholar
    for result in scholar_results:
        while isinstance(result, EagerResult) or isinstance(result, AsyncResult): # while result is not the last, do a step
            result = result.get()
        scholar_records.append(result)

    # wait for soap api client to finish
    wpk_records = wokws_data_result.get()

    logger.info("jobs returned results")

    ret = wpk_records, scholar_records

    return ret
