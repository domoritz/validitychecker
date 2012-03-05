from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('www.apps.validitychecker.views',
    url(r'^$', 'index', name='home'),
    url(r'^search/?$', 'results'),
    url(r'^status/(?P<query>.+)/$', 'status'),
    url(r'^score/?$', 'get_score'),
    url(r'^statistics/?$', 'statistics'),
)
