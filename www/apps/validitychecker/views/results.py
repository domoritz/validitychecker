from django.core.urlresolvers import reverse
from django.db.models import F, Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from random import shuffle, seed
import math

from datetime import date
import urllib

from www.apps.validitychecker.views import *

from www.apps.validitychecker.models import Query, Article, Author
from www.utils import parsers, IsiHandler, gviz_api

def results(request, query):

    qobj = Query.objects.get(query__iexact=query)

    if qobj.status in [Query.FINISHED]:

        resultset = authors_and_articles_for_query(qobj)

        return render_to_response('results.html',
                                  context_instance=RequestContext(request, dict(
                                  results=resultset, query=query)))
    else:
        return # 300 /index

def authors_and_articles_for_query(qobj):
    articles = qobj.articles.all() # articles for query

    # add .prefetch_related('articles') if supported by dango version
    authors = Author.objects.filter(articles__in=articles)\
        .annotate(isi_cites=Sum('articles__times_cited_on_isi'))\
        .annotate(number_articles=Count('articles'))\
        .order_by('-number_articles').distinct()[:200]
    for author in authors:
        articles_by_author = author.articles.filter(id__in=articles).order_by('-publish_date').all()
        tpl = (author, articles_by_author)
        tpl[0].score = author.number_articles
        yield tpl

def get_authors_and_articles_from_db(titles):
    """
    returns the matching articles and authors from the db that are credible
    param: title a list of strings
    """
    ret = []
    authors = Author.objects.filter(isi_score__gt=0, articles__title__in=titles).annotate(isi_cites=Sum('articles__times_cited_on_isi')).distinct()[:8]
    for author in authors:
        tmp = (author, Article.objects.filter(title__in=titles, author__name=author.name).order_by('-publish_date'))
        #calculate score
        if not tmp[0].isi_cites:
            tmp[0].isi_cites = 0
        tmp[0].score = int(math.log(tmp[0].isi_cites+1) + 2*tmp[0].isi_score)
        ret.append(tmp)
    ret = sorted(ret, key=lambda elem: -elem[0].score)
    return ret

@csrf_exempt
def get_score(request):
    title = request.POST.get('title')
    author = request.POST.get('author')
    import random
    return HttpResponse(str(random.randrange(100)), mimetype="text/plain")
