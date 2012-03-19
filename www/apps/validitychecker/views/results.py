#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models import F, Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

import urllib

from www.apps.validitychecker.views import *
from www.apps.validitychecker.models import Query, Article, Author

def results(request, query):

    query = urllib.unquote_plus(query)

    qobj = get_object_or_404(Query, query__iexact=query)

    if qobj.successful():

        qobj.count = F('count') + 1
        qobj.save()

        resultset = authors_and_articles_for_query(qobj)

        return render_to_response('results.html',
                                  context_instance=RequestContext(request, dict(
                                  results=resultset, query=query)))
    else:
        return # 300 /index

def authors_and_articles_for_query(qobj):
    """
    returns the matching articles and authors from the db that are credible
    """

    # get credible articles for query
    articles = qobj.articles.filter(is_credible=True).all() # articles for query

    # add .prefetch_related('articles') if supported by dango version
    authors = Author.objects.filter(articles__in=articles)\
        .annotate(isi_cites=Sum('articles__times_cited_on_isi'))\
        .annotate(number_articles=Count('articles'))\
        .order_by('-number_articles').distinct()[:8]
    for author in authors:
        articles_by_author = author.articles.filter(id__in=articles).order_by('-publish_date').all()
        tpl = (author, articles_by_author)
        tpl[0].score = author.number_articles
        yield tpl

@csrf_exempt
def get_score(request):
    title = request.POST.get('title')
    author = request.POST.get('author')
    import random
    return HttpResponse(str(random.randrange(100)), mimetype="text/plain")
