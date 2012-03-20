from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from www.apps.validitychecker.models import Article
from www.apps.validitychecker.utils import gviz_api

from datetime import date

def statistics(request):
    description = {"count": ("number", "Publications"),
                 "year": ("string", "Year")}
    #data_for_articles = [{'count': article['count'], 'year': article['publish_date'].year} for article in Article.objects.values('publish_date').annotate(count=Count('id')) if article['publish_date']]

    data = []
    years_count_db = list(Article.objects.values('publish_date').filter(publish_date__isnull=False).annotate(count=Count('id')).order_by('publish_date'))
    for year in range(1900, date.today().year+1):
        if years_count_db[0]['publish_date'].year == year:
            e = years_count_db.pop(0)
            data.append({'year': year, 'count':e['count']})
        else:
            data.append({'year': year, 'count':0})

    scatter_data_table = gviz_api.DataTable(description)
    scatter_data_table.LoadData(data)
    json = scatter_data_table.ToJSCode("data",columns_order=("year", "count"))

    return render_to_response('statistics.html',
                              {'scatter': json },
                              context_instance=RequestContext(request))
