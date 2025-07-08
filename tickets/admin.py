# tickets/admin.py
from django.contrib import admin
from .models import Ticket
from django.contrib.auth.models import User # Importez le modèle User de Django
from django.db.models import QuerySet # Importez QuerySet

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subject', 'status', 'priority', 'platform_name',
        'first_name', 'last_name', 'email', 'submission_date', 'agent_display'
    )
    list_filter = ('status', 'priority', 'platform_name', 'submission_date')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    # readonly_fields seront définis dynamiquement par get_readonly_fields

    fieldsets = (
        (None, {
            'fields': ('subject', 'message', 'platform_name')
        }),
        ('Informations du plaignant', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Statut et Priorité', {
            'fields': ('status', 'priority', 'agent')
        }),
        ('Dates', {
            'fields': ('submission_date',)
        }),
    )

    def agent_display(self, obj):
        if obj.agent:
            return f"{obj.agent.first_name} {obj.agent.last_name} ({obj.agent.username})"
        return "Non assigné"
    agent_display.short_description = 'Agent Assigné'

    # --- NOUVELLES FONCTIONNALITÉS ---

    # Méthode pour limiter les champs modifiables selon le rôle de l'utilisateur
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            # Un superutilisateur peut tout modifier (sauf la date de soumission si on veut)
            return ('submission_date',) # Seule la date de soumission est toujours en lecture seule
        else:
            # Pour un agent (non-superutilisateur), ces champs sont en lecture seule
            return (
                'first_name', 'last_name', 'email', 'platform_name',
                'submission_date', 'subject', 'message' # Ajout des champs du plaignant, sujet, message en lecture seule
            )

    # Méthode pour limiter les choix de statut dans la liste déroulante pour les agents
    # Cette méthode est appelée lors de l'affichage du formulaire d'édition
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            if request.user.is_superuser:
                # Un superutilisateur voit tous les choix possibles
                kwargs['choices'] = Ticket.STATUS_CHOICES
            else:
                # Pour un agent (non superutilisateur)
                current_status = None
                if 'instance' in kwargs and kwargs['instance'] is not None:
                    current_status = kwargs['instance'].status

                if current_status == 'nouveau':
                    # De 'nouveau', un agent peut passer à 'en cours de traitement' ou 'ignoré' (si autorisé)
                    kwargs['choices'] = [
                        ('nouveau', 'Nouveau'),
                        ('en cours de traitement', 'En cours de traitement'),
                        ('ignore', 'Ignoré'),
                        # Pour la transition 'résolu'/'achevé', on la mettra dans une action ou un bouton spécifique
                    ]
                elif current_status == 'en cours de traitement':
                    # De 'en cours de traitement', un agent peut passer à 'résolu'/'achevé' ou 'ignoré'
                    kwargs['choices'] = [
                        ('en cours de traitement', 'En cours de traitement'),
                        ('resolu', 'Résolu'), # Ou 'achevé' si c'est la valeur interne
                        ('ignore', 'Ignoré'),
                    ]
                else:
                    # Pour les statuts déjà résolus ou ignorés, l'agent ne peut pas les modifier
                    # Ou alors juste les re-voir, la liste peut être vide ou contenir juste le statut actuel
                    kwargs['choices'] = [(current_status, dict(Ticket.STATUS_CHOICES).get(current_status, current_status))]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    # Surcharge de save_model pour l'assignation automatique de l'agent
    def save_model(self, request, obj, form, change):
        # obj est l'instance du Ticket
        # form.initial['status'] est le statut AVANT modification
        # obj.status est le statut APRÈS modification

        # Vérifier si l'utilisateur est un agent (pas un superutilisateur)
        if not request.user.is_superuser:
            # Si le statut passe de 'nouveau' à 'en cours de traitement'
            if (form.initial and form.initial['status'] == 'nouveau' and
                    obj.status == 'en cours de traitement'):
                # Si le ticket n'est pas déjà assigné
                if not obj.agent:
                    obj.agent = request.user # Assignation automatique de l'agent connecté
                    # La date de prise en charge pourrait être ajoutée ici si vous avez un champ dédié

        super().save_model(request, obj, form, change) # Sauvegarde l'objet Ticket