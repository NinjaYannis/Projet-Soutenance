from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        # Spécifiez les champs qui peuvent être reçus via l'API.
        # L'ID, la date de soumission, le statut et la priorité par défaut sont gérés par le modèle.
        # L'agent n'est pas assigné à ce stade.
        fields = ['first_name', 'last_name', 'email', 'subject', 'message', 'platform_name']