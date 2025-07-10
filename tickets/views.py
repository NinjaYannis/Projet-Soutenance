# tickets/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter 
from django_filters.rest_framework import DjangoFilterBackend 
from django.db.models import Q

from .serializers import TicketSerializer
from projet.authentication import APIKeyAuthentication
from .models import Ticket


class TicketSubmitAPIView(APIView):
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [AllowAny] 

    def post(self, request, format=None):
        platform_name_from_auth = request.auth
        if not platform_name_from_auth:
            return Response({"detail": "Nom de plateforme non déterminé via l'API Key."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['platform_name'] = platform_name_from_auth 

        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TicketListAPIView(ListAPIView):
    queryset = Ticket.objects.all() 
    serializer_class = TicketSerializer 
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'platform_name', 'submission_date']
    search_fields = ['first_name', 'last_name', 'subject', 'message']
    ordering_fields = ['submission_date', 'priority', 'status', 'id']
    ordering = ['-submission_date'] 

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(Q(agent=self.request.user) | Q(agent__isnull=True))
        return queryset

class TicketDetailAPIView(RetrieveAPIView):
    queryset = Ticket.objects.all() 
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(Q(agent=self.request.user) | Q(agent__isnull=True))
        return queryset
    

class IsSuperuserOrAssignedAgent(BasePermission):
    message = "Vous n'avez pas la permission de modifier ce ticket ou de l'assigner."

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
 
        if obj.agent == request.user: 
            return True
        
        if obj.agent is None and request.method in ['PUT', 'PATCH']:
            # L'agent peut s'assigner un ticket non assigné
            # Vérifier si 'agent_id' est dans les données et correspond à l'utilisateur
            if 'agent_id' in request.data and request.data['agent_id'] == request.user.id:
                return True
            # Refuser si l'agent tente de modifier un ticket non assigné sans s'assigner
            # ou de l'assigner à quelqu'un d'autre.
            return False 

        return False


class TicketUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrAssignedAgent] 

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        data = request.data.copy()

        # Logique d'assignation automatique de l'agent si le statut passe de 'nouveau' à 'en cours de traitement'
        # et que le ticket n'est pas encore assigné.
        # On injecte l'ID de l'agent dans les données sous le champ 'agent_id' (le champ d'input du serializer).
        if not request.user.is_superuser and \
           instance.status == 'nouveau' and \
           data.get('status') == 'en cours de traitement' and \
           not instance.agent:
            data['agent_id'] = request.user.id # Utilisez 'agent_id' ici pour correspondre au serializer

        # Le serializer va maintenant gérer la mise à jour de l'agent via 'agent_id'
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save() # Le serializer.update() par défaut gérera l'assignation de l'agent via agent_id

        return Response(serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(Q(agent=self.request.user) | Q(agent__isnull=True))
        return queryset