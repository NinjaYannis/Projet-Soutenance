from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    agent = serializers.PrimaryKeyRelatedField(queryset=User.objects.none(), required=False)

    class Meta:
        model = Ticket
        fields = [
            'first_name', 'last_name', 'email', 'subject', 'message',
            'platform_name', 'status', 'priority', 'agent'  #  Ajout des champs manquants
        ]
        read_only_fields = ['platform_name', 'priority']  #  On ne laisse pas modifier depuis le formulaire

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and not request.user.is_superuser:
            self.fields['agent'].queryset = User.objects.filter(id=request.user.id)
        elif request:
            self.fields['agent'].queryset = User.objects.all()

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

        validated_data['priority'] = priority  #  On force la priorité ici
        return super().create(validated_data)
