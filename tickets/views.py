from django.shortcuts import render
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket # Assurez-vous d'importer votre modèle Ticket
from .serializers import TicketSerializer


class TicketSubmitAPIView(APIView):
    def post(self, request, format=None):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            # La logique de priorité est maintenant dans la méthode create du serializer.
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)