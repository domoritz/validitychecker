#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson

from www.apps.validitychecker.views import *
from www.apps.validitychecker.models import Query

from www.apps.scrapers.tasks import CrawlScholarTask, FetchWokmwsTask

def status(request, query):
    """
    returns the status of a query
    see 'class Query' for more information
    """

    qobj, created = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})

    #c = CrawlScholarTask()
    #c.run(query=query, number=10, qobj=qobj)

    if created or qobj.status in [Query.INVALID]:
        #queue query
        try:
            #CrawlScholarTask.delay(query=query, number=10, qobj=qobj)
            FetchWokmwsTask.delay(query=query, qobj=qobj, number=100)
        except Exception, e:
            qobj.status = Query.ERROR
            qobj.message = str(e)
            qobj.save()

    qobj = Query.objects.get(query__iexact=query)

    querystatus = Query.QUERY_STATUS[int(qobj.status)][1]
    querymessage = qobj.message

    statusdict = {
        'status' : querystatus,
        'message' : querymessage,
        'resulturl' : '/results/'+query,
    }

    return HttpResponse(simplejson.dumps(statusdict), mimetype='application/json')
