from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return None

        if api_key not in settings.API_KEYS:
            raise AuthenticationFailed('Clé API invalide.')

        return (None, settings.API_KEYS[api_key])