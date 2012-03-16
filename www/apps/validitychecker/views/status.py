#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson

import urllib

from www.apps.validitychecker.models import Query
from www.apps.validitychecker.tasks import fetch_soap, scrape_scolar

def status(request, query):
    """
    returns the status of a query
    see 'class Query' for more information
    """

    query = urllib.unquote_plus(query)

    qobj, created = Query.objects.get_or_create(query__iexact=query, defaults={'query':query})

    #c = CrawlScholarTask()
    #c.run(query=query, number=10, qobj=qobj)

    # starting reactor
    #threaded_reactor()

    if created or qobj.status in [Query.INVALID]:
        #queue query
        try:
            fetch_soap.delay(query=query, number=10, qobj=qobj)
            scrape_scolar.delay(query=query, number=10, qobj=qobj)

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
        'resulturl' : '/results/'+urllib.quote_plus(query),
    }

    return HttpResponse(simplejson.dumps(statusdict), mimetype='application/json')
