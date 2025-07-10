# tickets/serializers.py
from rest_framework import serializers
from .models import Ticket
from django.contrib.auth.models import User

# Serializer pour les informations de base de l'agent (pour la sortie)
class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

# Serializer pour le modèle Ticket
class TicketSerializer(serializers.ModelSerializer):
    # Ce champ 'agent' est pour la *sortie* (quand on lit un ticket).
    # Il utilise AgentSerializer pour afficher les détails complets de l'agent.
    agent = AgentSerializer(read_only=True)

    # Ce nouveau champ 'agent_id' est pour l'*entrée* (quand on envoie un ID d'agent pour l'assigner).
    # PrimaryKeyRelatedField sait comment prendre un ID et le lier à une instance de modèle.
    # source='agent' indique que ce champ d'entrée correspond au champ 'agent' du modèle.
    # write_only=True signifie qu'il est utilisé seulement pour l'écriture (input), pas pour la lecture (output).
    # required=False et allow_null=True permettent de ne pas rendre l'assignation obligatoire.
    agent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='agent', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Ticket
        # Incluez 'agent' pour la sortie et 'agent_id' pour l'entrée.
        # 'agent' est marqué comme read_only via extra_kwargs pour s'assurer qu'il n'est pas utilisé en entrée.
        fields = ['id', 'first_name', 'last_name', 'email', 'subject', 'message', 'platform_name', 'status', 'priority', 'submission_date', 'agent', 'agent_id']
        extra_kwargs = {
            'agent': {'read_only': True}
        }

    def create(self, validated_data):
        # La logique de création est inchangée.
        # Si 'agent_id' est passé à la création, ModelSerializer le gérera automatiquement.
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

    # La méthode update par défaut de ModelSerializer gérera maintenant
    # la mise à jour du champ 'agent' via 'agent_id' dans validated_data.
    # Nous n'avons plus besoin de surcharger update ici.
    # Supprimez votre méthode 'update' personnalisée de cette classe.