from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.filters import SearchFilter, OrderingFilter 
from django_filters.rest_framework import DjangoFilterBackend 
from .serializers import TicketSerializer
from projet.authentication import APIKeyAuthentication
from .models import Ticket
from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView 
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission 
from .serializers import TicketSerializer
from projet.authentication import APIKeyAuthentication


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
            if 'agent' in request.data and request.data['agent'] == request.user.id:
                return True
            
            return False 

        return False


class TicketUpdateAPIView(RetrieveUpdateAPIView): 
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrAssignedAgent] 

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(Q(agent=self.request.user) | Q(agent__isnull=True))
        return queryset