from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('apps.validitychecker.urls')),
)

urlpatterns += patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

from django.views.generic.simple import direct_to_template
urlpatterns += patterns('',
    (r'^robots\.txt$', direct_to_template,
     {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^humans\.txt$', direct_to_template,
     {'template': 'humans.txt', 'mimetype': 'text/plain'}),
    (r'^crossdomain\.xml$', direct_to_template,
     {'template': 'crossdomain.xml', 'mimetype': 'text/xml'}),
)
