from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TicketSerializer
from .models import Ticket # Assurez-vous d'importer votre modèle Ticket

class TicketSubmitAPIView(APIView):
    def post(self, request, format=None):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            # Le statut et la priorité par défaut sont gérés par le modèle Ticket.
            # La logique d'assignation automatique de priorité sera ajoutée plus tard.
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)