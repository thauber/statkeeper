from django.shortcuts import render_to_response
from django.template import RequestContext

def stat_keeper(request):
    return render_to_response(
        'stat_keeper/stat_keeper.html',
        {},
        context_instance=RequestContext(request)
    )
