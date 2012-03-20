#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson
from django.core.urlresolvers import reverse
import logging

from www.apps.validitychecker.models import Query
from www.apps.validitychecker.tasks import combined_data_retrieve

import urllib

def status(request, query):
    """
    returns the status of a query
    see 'class Query' for more information
    """
    logger = logging.getLogger(__name__)

    query = urllib.unquote_plus(query)

    qobj, created = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})

    if created or qobj.failed():
        result = combined_data_retrieve.delay(number=100, qobj=qobj)
        logger.info('running a task with the id %s for the query "%s"' % (result.task_id, query))

    querymessage = str(qobj.result()) if qobj.failed() else ''
    errtype = type(qobj.result()).__name__ if qobj.failed() else ''

    statusdict = {
        'status' : qobj.state(),
        'error' : errtype,
        'message' : querymessage,
        'resulturl' : reverse('results-view', kwargs={'query': urllib.quote_plus(query)}),
    }

    return HttpResponse(simplejson.dumps(statusdict), mimetype='application/json')
