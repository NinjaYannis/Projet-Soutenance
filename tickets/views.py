from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

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