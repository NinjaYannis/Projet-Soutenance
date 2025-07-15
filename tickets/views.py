from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, permissions #temporairement ouvert à tous pour test
#
from rest_framework import viewsets
from .models import Ticket
from .serializers import TicketSerializer
#
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



from .serializers import TicketSerializer
from projet.authentication import APIKeyAuthentication

class TicketSubmitAPIView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [AllowAny] 

    
    @swagger_auto_schema(
        request_body=TicketSerializer,
        responses={
        201: openapi.Response('Ticket créé avec succès', TicketSerializer),
        400: 'Erreur de validation ',
        },
        operation_description="Soumettre un ticket avec le nom de la plateforme déterminé par l'API Key."
        )
    #---------------
    def post(self, request, format=None):
        platform_name_from_auth= request.auth
        if not platform_name_from_auth:
            return Response({"detail": "Nom de plateforme non déterminé via l'API Key."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['platform_name'] = platform_name_from_auth 

        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]  # Uniquement les utilisateurs connectés

    def perform_update(self, serializer):
        ticket = self.get_object()
        user = self.request.user

        ancien_statut = ticket.status
        nouveau_statut = self.request.data.get('status', ancien_statut)

        # Règles de transitions autorisées
        transitions_valides = {
            'nouveau': ['en cours de traitement', 'résolu', 'ignoré'],
            'en cours de traitement': ['résolu', 'ignoré'],
            'résolu': [],
            'ignoré': [],
        }

        if nouveau_statut not in transitions_valides.get(ancien_statut, []):
            raise serializers.ValidationError(
                f"Impossible de passer de {ancien_statut} à {nouveau_statut}."
            )

        # Si l'agent n'était pas encore défini OU s'il essaie de changer d'agent
        if ticket.agent is None or ticket.agent == user:
            serializer.save(agent=user)
        else:
            raise serializers.ValidationError("Vous ne pouvez pas réassigner un ticket déjà assigné.")
