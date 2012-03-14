#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from random import shuffle, seed
import urllib

from www.apps.validitychecker.models import Query

def index(request):
    popular_queries = list(Query.objects.filter(status=Query.FINISHED).order_by('-count')[:20])
    seed(42)
    shuffle(popular_queries)
    for q in popular_queries:
        q.url = urllib.quote_plus(q.query)

    return render_to_response('home.html',
                              { 'popular_queries': popular_queries },
                              context_instance=RequestContext(request))
