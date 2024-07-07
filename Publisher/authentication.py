from django.contrib.auth.backends import BaseBackend
from Publisher.models import Publisher  # Adjust import based on your app structure

class PublisherBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            publisher = Publisher.objects.get(username=username)

            if publisher.check_password(password):
                return publisher
            else:
                return None
        except Publisher.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Publisher.objects.get(pk=user_id)
        except Publisher.DoesNotExist:
            return None
