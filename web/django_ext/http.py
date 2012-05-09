import re
import simplejson
 
from django.http import HttpResponse
from django.conf import settings

 
class JSONResponse(HttpResponse):
    def __init__(self, request, data):
        indent = 2 if settings.DEBUG else None
        mime = "text/javascript" if settings.DEBUG else "application/json"
        content = simplejson.dumps(data, indent=indent)
        callback = request.GET.get('callback')
        if callback:
            # verify that the callback is secure
            if re.compile(r'^[a-zA-Z][\w.]*$').match(callback):
                content = '%s(%s);' % (callback, content)
        super(JSONResponse, self).__init__(
            content = content,
            mimetype = mime,
        )