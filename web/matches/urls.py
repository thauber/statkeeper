from django.conf.urls.defaults import patterns, include, url
from views import *

urlpatterns = patterns('',
    # url(r'^$', 'web.views.home', name='home'),
    url(r'^$', handle_match),
    url(r'^(\d+)/?$', handle_match),
    url(r'^(\d+)/actions/?$', handle_action),
    url(r'^(\d+)/actions/(\d+)/?$', handle_action),
    url(r'^(\d+)/player/([A-Za-z-_]+)/?$', handle_match_player),
    url(r'^(\d+)/player/([A-Za-z-_]+)/(\d+)/?$', handle_match_player),
    url(r'^sk/?$', stat_keeper),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
