
from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        # Spécifiez les champs qui peuvent être reçus via l'API.
        # L'ID, la date de soumission, le statut et la priorité par défaut sont gérés par le modèle.
        # L'agent n'est pas assigné à ce stade.
        model = Ticket
        fields = ['first_name', 'last_name', 'email', 'subject', 'message']

    def create(self, validated_data):
        subject = validated_data.get('subject', '').lower()
        priority = 'basse'

        critical_keywords = [
            'erreur serveur', 'site inaccessible', 'impossible de se connecter',
            'page blanche', 'plantage', 'panne', 'données perdues', 'piratage',
            'fuite de données', 'problème de sécurité', 'transaction échouée',
            'paiement non reçu', 'compte bloqué', 'urgent', 'bloqué', 'crash',
            'downtime', 'plus rien ne fonctionne', 'non fonctionnel', 'brisé', 'cassé'
        ]

        medium_keywords = [
            'lent', 'lenteur', 'fonctionne mal', 'bug mineur', 'erreur d’affichage',
            'incohérence', 'mauvais alignement', 'champ manquant', 'bouton ne répond pas',
            'pas à jour', 'problème d’interface', 'traduction incorrecte', 'police illisible',
            'message d’erreur', 'navigabilité difficile', 'formulaire incomplet',
            'déconnexion aléatoire', 'image non chargée'
        ]

        if any(keyword in subject for keyword in critical_keywords):
            priority = 'critique'
        elif any(keyword in subject for keyword in medium_keywords):
            priority = 'moyenne'

        ticket = Ticket.objects.create(priority=priority, **validated_data)
        return ticket