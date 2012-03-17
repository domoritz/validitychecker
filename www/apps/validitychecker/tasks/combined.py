#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
In contrast to crawling/scraping these tasks will use apis such as soap in order to retrieve the information

The soap client will not save the data to the database so we have to do it here.
"""

from django.db import transaction

from celery.task import task, subtask
from celery.task.sets import TaskSet

from www.apps.validitychecker.models import Query, Article, Author, KeyValue

from www.apps.validitychecker.tasks import fetch_soap, scrape_scolar

#@transaction.commit_on_success
@task(name='get data for query and write to db')
def combined_data_retrieve(query="solar flares", number = 10, qobj=None):

    logger = combined_data_retrieve.get_logger()
    logger.info("Start retrieving data")

    # start tasks
    tasks = [
        #fetch_soap.subtask(query, number, qobj),
        scrape_scolar.subtask((query, number, qobj)),
    ]

    job = TaskSet(tasks=tasks)

    result = job.apply_async()

    #result.ready()  # have all subtasks completed?
    #result.successful() # were all subtasks successful?
    result.join()
