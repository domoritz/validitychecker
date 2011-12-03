from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from validitychecker.models import Query, Article, Author, Language, Datatype
from datetime import date
from django.db.models import F
import urllib
from validitychecker.helpers import parsers

def results(request):
    if 'q' in request.GET:
        query = request.GET['q']

        #save query to db
        qobj, created = Query.objects.get_or_create(query=query, defaults={'query':query, 'number':0})
        qobj.number = F('number') + 1
        qobj.save()

        #query google scholar
        googleScholar = parsers.google_scholar_parser(query)

        #write to db
        articleType, created = Datatype.objects.get_or_create(name='article', defaults={'name':'article'})
        for entry in googleScholar:
            article, created = Article.objects.get_or_create(
                title=entry['title'],
                defaults={
                    'url':entry['url'], 
                    'publish_date':entry['publish_date'],
                    'title':entry['title'], 
                    'data_type':articleType
                })
            for authorName in entry['authors']:
                author, created = Author.objects.get_or_create(name=authorName, defaults={'name':authorName})
                author.articles.add(article)

        titles = [x['title'] for x in googleScholar]

        resultset = get_authors_and_articles_from_db(titles)
        #resultset = get_fake_results(query)

        return render_to_response('results.html',
                                  context_instance=RequestContext(request, dict(
                                  target=reverse(results), results=resultset, query=query)))
    else:
        return # 300 /index

def get_authors_and_articles_from_db(titles):
    """ 
    returns the matching articles and authors from the db 
    param: title a list of strings    
    """
    authors = Author.objects.filter(articles__title__in=titles).distinct()[0:10]
    ret = [(author,Article.objects.filter(title__in=titles).filter(author__name=author.name).order_by('-publish_date')) for author in authors]
    #ret = Article.objects.filter(title__in=titles).values('author')
    #ret = Author.objects.filter(articles__title__in=titles).
    #print ret
    return ret

def index(request):
    popular_queries = Query.objects.order_by('-number')[:5]
    for q in popular_queries:
        q.url = urllib.quote_plus(q.query) 
    
    return render_to_response('home.html',
                              { 'popular_queries': popular_queries },
                              context_instance=RequestContext(request, dict(
                              target=reverse(results))))
