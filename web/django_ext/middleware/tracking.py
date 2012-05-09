import uuid
import datetime
import hmac

from django.conf import settings

# http://www.google.com/search?q=10+years+in+seconds
TEN_YEARS = 315569260

class TrackingMiddleware(object):
    
    def process_request(self, request):
        trk = request.COOKIES.get(settings.TRACKING_COOKIE_NAME)
        
        if trk is not None:
            cookie, _, digest = trk.rpartition(' ')
            digest_verify = hmac.new(settings.SECRET_KEY, cookie).hexdigest()
            if digest != digest_verify:
                trk = None
            else:
                request._set_trk = False
        
        if trk is None:
            cookie = str(datetime.datetime.utcnow()) + ' ' + str(uuid.uuid1())
            digest = hmac.new(settings.SECRET_KEY, cookie).hexdigest()
            request._set_trk = cookie + ' ' + digest
        
        request.uuid = cookie.rpartition(' ')[2]
        request.trk = trk or request._set_trk
    
    def process_response(self, request, response):
        if getattr(request, '_set_trk', None):
            expires = datetime.datetime.strftime(
                datetime.datetime.utcnow() +
                    datetime.timedelta(seconds=TEN_YEARS),
                "%a, %d-%b-%Y %H:%M:%S GMT"
            )
            response.set_cookie(settings.TRACKING_COOKIE_NAME,
                request._set_trk, expires=expires, max_age=TEN_YEARS)
        return response