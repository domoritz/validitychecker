from django.http import HttpResponse
from django.utils import simplejson

from www.apps.validitychecker.views import *
from www.apps.validitychecker.models import Query

def status(request, query):
    """
    returns the status of a query
    see 'class Query' for more information
    """

    qobj, created = Query.objects.get_or_create(query=query, defaults={'query':query})

    if created or qobj.status is Query.INVALID:
        #queue query
        qobj.status = Query.QUEUED
        qobj.save()

    querystatus = Query.QUERY_STATUS[int(qobj.status)]
    status = {
        'status' : querystatus,
        'resulturl' : '/results/'+query,
    }

    return HttpResponse(simplejson.dumps(status), mimetype='application/json')
