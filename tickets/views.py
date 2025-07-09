
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication # Pour les tests admin Django
from rest_framework.permissions import AllowAny # Pour autoriser l'accès non authentifié de base pour les tests API (sera modifié)

from .serializers import TicketSerializer
from .models import Ticket
from projet.authentication import APIKeyAuthentication # Importez votre classe d'authentification personnalisée

class TicketSubmitAPIView(APIView):
    # Utilise votre authentification personnalisée
    # Désactivez SessionAuthentication et BasicAuthentication si vous ne voulez que APIKeyAuthentication
    authentication_classes = [APIKeyAuthentication] # N'utilisez que APIKeyAuthentication pour la production
    permission_classes = [AllowAny] # Pour permettre l'accès si APIKeyAuthentication réussit

    def post(self, request, format=None):
        # request.auth contiendra le nom de la plateforme si APIKeyAuthentication a réussi
        platform_name_from_auth = request.auth
        if not platform_name_from_auth:
            return Response({"detail": "Nom de plateforme non déterminé via l'API Key."}, status=status.HTTP_400_BAD_REQUEST)

        # Crée un dictionnaire mutable pour les données
        data = request.data.copy()
        data['platform_name'] = platform_name_from_auth # Remplissage automatique

        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)