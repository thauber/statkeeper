from django.conf.urls.defaults import patterns, include, url
from views import *

urlpatterns = patterns('',
    # url(r'^$', 'web.views.home', name='home'),
    url(r'^sk/', stat_keeper),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
