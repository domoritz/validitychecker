from django.core.urlresolvers import reverse
from django.db.models import F, Count, Sum
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from random import shuffle, seed

from www.apps.validitychecker.views import results

from www.apps.validitychecker.models import Query, Article, Author
from www.utils import parsers, IsiHandler, gviz_api
import urllib

def statistics(request):
    description = {"publications": ("number", "Publications"),
                 "cg_score": ("number", "Climate Goggles Score"),
                 "isi_score": ("number", "Isi Score")}
    data = [{'isi_score': author.isi_score, 'publications': author.publications} for author  in Author.objects.annotate(publications=Count('articles'))]
    scatter_data_table = gviz_api.DataTable(description)
    scatter_data_table.LoadData(data)
    json = scatter_data_table.ToJSCode("data",columns_order=("publications", "cg_score", "isi_score"))

    return render_to_response('statistics.html',
                              {'scatter': json },
                              context_instance=RequestContext(request, dict(target=reverse(results))))
