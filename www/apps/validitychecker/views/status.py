#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse

from celery.result import AsyncResult

from www.apps.validitychecker.models import Query
from www.apps.validitychecker.tasks import combined_data_retrieve

import urllib

def status(request, query):
    """
    returns the status of a query
    see 'class Query' for more information
    """

    query = urllib.unquote_plus(query)

    qobj, created = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})

    if created or qobj.failed():
        task = combined_data_retrieve.delay(number=10, qobj=qobj)
        #save task.task_id
        qobj.task_id = task.task_id
        qobj.save()

    querymessage = str(qobj.result()) if qobj.failed else ''
    errtype = type(qobj.result()).__name__ if qobj.failed else ''

    statusdict = {
        'status' : AsyncResult(qobj.task_id).status,
        'error' : errtype,
        'message' : querymessage,
        'resulturl' : reverse('status-view', kwargs={'query': urllib.quote_plus(query)}),
    }

    return HttpResponse(simplejson.dumps(statusdict), mimetype='application/json')
