from django.conf.urls.defaults import patterns, include, url
from views import *

urlpatterns = patterns('',
    # url(r'^$', 'web.views.home', name='home'),

    url(r'detail/([A-Za-z0-9-_]+)/([A-Za-z0-9-_]+)/([A-Za-z0-9-_]+)/([A-Za-z0-9-_]+)/([A-Za-z-0-9_]+)/?$',
        match_detail, name="match-detail"),
    url(r'detail/([A-Za-z0-9-_]+)/([A-Za-z0-9-_]+)/([A-Za-z-0-9_]+)/?$',
        tournament_detail,
        name="tournament-detail"),
    url(r'quick_add/?$', quick_add, name="quick-add"),
    url(r'create/?$', create_select_tournament, name="create-match"),
    url(r'create/(\d+)/?$', create_match, name="create-match"),
    url(r'swapsides/(\d+)?$', swapsides_game, name="game-swap-sides"),
    url(r'create_next/(\d+)?$', create_next_game, name="game-create-next"),
    url(r'change_map/(\d+)?$', change_game_map, name="game-change-map"),
    url(r'^(\d+)/?$', handle_game),
    url(r'^(\d+)/actions/?$', handle_action),
    url(r'^(\d+)/actions/(\d+)/?$', handle_action),
    url(r'^(\d+)/player/([A-Za-z-_]+)/?$', handle_game_player),
    url(r'^(\d+)/player/([A-Za-z-_]+)/(\d+)/?$', handle_game_player),
    url(r'^sk/(\d+)/?$', stat_keeper, name="stat-keeper"),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
