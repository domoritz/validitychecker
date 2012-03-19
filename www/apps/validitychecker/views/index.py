#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from random import shuffle, seed
import urllib

from www.apps.validitychecker.models import Query

def index(request):
    popular_queries = list(Query.objects.order_by('-count')[:30])
    popular_successful_queries = [x for x in popular_queries if x.successful()][:20]

    seed(42)
    shuffle(popular_successful_queries)
    for q in popular_successful_queries:
        q.url = urllib.quote_plus(q.query)

    return render_to_response('home.html',
                              { 'popular_queries': popular_successful_queries },
                              context_instance=RequestContext(request))
