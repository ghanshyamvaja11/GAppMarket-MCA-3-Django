from django.contrib.auth.backends import BaseBackend
from Administrator.models import Administrator  # Adjust import based on your app structure

class AdministratorBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            admin = Administrator.objects.get(username=username)

            if admin.check_password(password):
                return admin
            else:
                return None
        except Administrator.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Administrator.objects.get(pk=user_id)
        except Administrator.DoesNotExist:
            return None
