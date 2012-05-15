from django.conf.urls.defaults import patterns, include, url
from views import *

urlpatterns = patterns('',
    # url(r'^$', 'web.views.home', name='home'),

    url(r'create/?$', create_match),
    url(r'swapsides/(\d+)?$', swapsides_match, name="match-swap-sides"),
    url(r'create_next/(\d+)?$', create_next_match, name="match-create-next"),
    url(r'change_map/(\d+)?$', change_match_map, name="match-change-map"),
    url(r'^(\d+)/?$', handle_match),
    url(r'^(\d+)/actions/?$', handle_action),
    url(r'^(\d+)/actions/(\d+)/?$', handle_action),
    url(r'^(\d+)/player/([A-Za-z-_]+)/?$', handle_match_player),
    url(r'^(\d+)/player/([A-Za-z-_]+)/(\d+)/?$', handle_match_player),
    url(r'^sk/(\d+)/?$', stat_keeper, name="stat-keeper"),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
