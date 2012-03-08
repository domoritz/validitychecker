#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson

from www.apps.validitychecker.views import *
from www.apps.validitychecker.models import Query

from www.apps.scrapers.tasks import CrawlScholarTask

def status(request, query):
    """
    returns the status of a query
    see 'class Query' for more information
    """

    qobj, created = Query.objects.get_or_create(query=query, defaults={'query':query})

    if created or qobj.status in [Query.INVALID, Query.ERROR]:
        #queue query
        try:
            CrawlScholarTask.delay(query=query, number=10, qobj=qobj)
        except Exception, e:
            qobj.status = Query.ERROR
            qobj.message = str(e)
            qobj.save()

    qobj = Query.objects.get(query=query)

    querystatus = Query.QUERY_STATUS[int(qobj.status)]
    querymessage = qobj.message

    status = {
        'status' : querystatus,
        'message' : querymessage,
        'resulturl' : '/results/'+query,
    }

    return HttpResponse(simplejson.dumps(status), mimetype='application/json')
