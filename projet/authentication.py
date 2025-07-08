# projet/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings # Pour accéder à vos API_KEYS depuis settings.py

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key') # Récupère la clé depuis l'en-tête X-API-Key

        if not api_key:
            return None # Pas de clé API fournie

        if api_key not in settings.API_KEYS:
            raise AuthenticationFailed('Clé API invalide.')

        # Si la clé est valide, on retourne un tuple (user, auth)
        # Pour une clé API, l'utilisateur est souvent None ou un User dédié
        # et 'auth' est la clé elle-même ou le nom de la plateforme.
        # Ici, on passe le nom de la plateforme pour pouvoir le récupérer dans la vue.
        return (None, settings.API_KEYS[api_key]) # (user, auth)