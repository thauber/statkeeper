from django.conf.urls.defaults import patterns, include, url
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    url(r'^matches/', include('web.matches.urls')),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
        {'document_root': settings.MEDIA_ROOT,})
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
