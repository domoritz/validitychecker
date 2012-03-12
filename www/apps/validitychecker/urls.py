from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('www.apps.validitychecker.views',
    url(r'^$', 'index', name='home'),
    url(r'^results/(?P<query>.+)$', 'results', name='results-view'),
    url(r'^status/(?P<query>.+)$', 'status', name='status-view'),
    url(r'^score/?$', 'get_score'),
    url(r'^statistics/?$', 'statistics'),
)
