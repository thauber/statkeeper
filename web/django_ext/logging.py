import socket
import time

import simplejson

from django.conf import settings

def log_event(logger, event, request=None, data=None,
    # Hostname and flavor like this for performance hack
    _hostname=socket.gethostname(), _flavor=settings.FLAVOR):
    if request.path.startswith('/admin'):
        return
    if not data:
        data = {}
    data.update({
        'event': event,
        'ts': time.time(),
        'hostname': _hostname,
        'flavor': _flavor,
    })
    has_session = getattr(request, 'session', None)
    if request:
        data.update({
            'uuid': getattr(request, 'uuid', None),
            'trk': getattr(request, 'trk', None),
        })
        if has_session and request.user.is_authenticated():
            data.update({
                'user_id': request.user.id,
                'username': request.user.username,
            })
    logger.info(simplejson.dumps(data))
