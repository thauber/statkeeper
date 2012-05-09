import logging
import time

from django_ext.logging import log_event

logger = logging.getLogger(__name__)

class LoggingMiddleware(object):
    
    def process_request(self, request):
        request._start_time = time.time()
        request.META['REMOTE_ADDR'] = request.META.get('HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR', ''))

    def process_response(self, request, response):
        # Bail out early for admin, since we really don't care about that
        if request.path.startswith('/admin'):
            return response
        elapsed = time.time() - request._start_time
        log_event(logger, 'webrequest', request, {
            'method': request.method,
            'url': request.build_absolute_uri(),
            'elapsed': elapsed,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'client_ip': request.META.get('REMOTE_ADDR'),
            'referer': request.META.get('HTTP_REFERER'),
            'response_size': len(response.content),
            'response_status': response.status_code,
            'uuid': getattr(request, 'uuid', None),
            'trk': getattr(request, 'trk', None),
        })
        return response
