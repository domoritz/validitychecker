from django.db.models import Count
from django.shortcuts import render_to_response
from django.template import RequestContext

from www.apps.validitychecker.models import Author

from www.apps.validitychecker.utils import gviz_api

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
                              context_instance=RequestContext(request))
