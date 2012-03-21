#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

#from django.db import transaction

from celery.result import AsyncResult, EagerResult
from celery.task import task, subtask
#from celery.task.sets import TaskSet

from www.apps.validitychecker.tasks.scrape import make_scholar_urls, fetch_page_from_url, parse_scholar_page
from www.apps.validitychecker.tasks.scrape import parse_wok_page, get_wok_page
from www.apps.validitychecker.tasks.fetch import prepare_client, search_soap, extract_data, wok_soap_complete
from www.apps.validitychecker.tasks.db import store_in_db

#@transaction.commit_on_success
@task(time_limit=90, name="combined.combined_data_retrieve")
def combined_data_retrieve(query=None, number=10, qobj=None):

    logger = combined_data_retrieve.get_logger()
    logger.info("Start retrieving data")

    # save task id
    qobj.task_id = combined_data_retrieve.request.id
    qobj.save()

    #raise Exception

                            # fetch more scholar because it's fast
    scholarurls = make_scholar_urls(qobj=qobj, number=2*number)

    #########
    # non blocking
    #########

    # run wok/isi fetching and parsing
    wok_result = get_wok_page.delay(qobj=qobj, number=number,
            callback=subtask(parse_wok_page,
            callback=subtask(store_in_db, credible=True)))

    # run scholar fetching and parsing
    scholar_results = [
            fetch_page_from_url.delay(url=url, qobj=qobj,
            callback=subtask(parse_scholar_page,
            callback=subtask(store_in_db, credible=False)))
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

    #wait for fetching and parsing of isi/wok
    while isinstance(wok_result, EagerResult) or isinstance(wok_result, AsyncResult): # while result is not the last, do a step
        wok_result = wok_result.get()
    wok_records = wok_result

    # wait for soap api client to finish
    wok_api_records = wokws_data_result.get()

    logger.info("jobs returned results")

    ret = { "stats":
            {
                "isi": len(wok_records),
                "isi api":len(wok_api_records),
                "scholar":len(scholar_records)
            },
            "isi":wok_records,
            "isi api":wok_api_records,
            "scholar":scholar_records,
        }

    return ret
