from django.contrib.auth.backends import ModelBackend as OriginalModelBackend

from django.contrib.auth.models import User

class ModelBackend(OriginalModelBackend):
    
    def get_user(self, user_id):
        try:
            return User.objects.select_related('profile').get(pk=user_id)
        except User.DoesNotExist:
            return None