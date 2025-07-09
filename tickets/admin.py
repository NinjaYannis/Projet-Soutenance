# tickets/admin.py
from django.contrib import admin
from django.contrib import messages # Pour les messages de succès dans l'admin
from .models import Ticket
from django.contrib.auth.models import User # Importez le modèle User de Django
from .forms import TicketAdminForm # IMPORTEZ VOTRE NOUVEAU FORMULAIRE ICI


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subject', 'status', 'priority', 'platform_name',
        'first_name', 'last_name', 'email', 'submission_date', 'agent_display'
    )
    list_filter = ('status', 'priority', 'platform_name', 'submission_date')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    # readonly_fields seront définis dynamiquement par get_readonly_fields (donc pas besoin de le lister statiquement ici)

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

    # --- Utilisation du formulaire personnalisé ---
    form = TicketAdminForm

    # --- Surcharge de get_form pour passer l'objet request au formulaire ---
    # C'est nécessaire pour que le formulaire puisse accéder à request.user
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request # Passe l'objet request au formulaire
        return form


    def agent_display(self, obj):
        if obj.agent:
            return f"{obj.agent.first_name} {obj.agent.last_name} ({obj.agent.username})"
        return "Non assigné"
    agent_display.short_description = 'Agent Assigné'

    # --- Méthode pour limiter les champs modifiables selon le rôle de l'utilisateur (inchangée) ---
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('submission_date',)
        else:
            return (
                'first_name', 'last_name', 'email', 'platform_name',
                'submission_date', 'subject', 'message'
            )

    # --- SUPPRIMER CE BLOC formfield_for_choice_field ---
    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     # ... (TOUT LE CODE DE CETTE MÉTHODE SERA SUPPRIMÉ D'ICI) ...
    #     return super().formfield_for_choice_field(db_field, request, **kwargs)
    # --- FIN DE LA SUPPRESSION ---

    # --- Surcharge de save_model pour l'assignation automatique de l'agent (inchangée) ---
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    # --- Action d'Administration Personnalisée (inchangée) ---
    actions = ['mark_as_in_progress_and_assign'] # Enregistre l'action dans l'admin

    def mark_as_in_progress_and_assign(self, request, queryset):
        tickets_to_update = queryset.filter(status='nouveau', agent__isnull=True)
        updated_count = 0
        for ticket in tickets_to_update:
            ticket.status = 'en cours de traitement'
            ticket.agent = request.user # Assignation automatique de l'agent connecté
            ticket.save() # Sauvegarde chaque ticket individuellement
            updated_count += 1

        if updated_count > 0:
            self.message_user(request, f"{updated_count} ticket(s) marqué(s) 'en cours de traitement' et assigné(s).", messages.SUCCESS)
        else:
            self.message_user(request, "Aucun ticket 'nouveau' non assigné n'a été sélectionné pour cette action.", messages.WARNING)
        
    mark_as_in_progress_and_assign.short_description = "Marquer comme 'en cours' et m'assigner"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            if 'mark_as_in_progress_and_assign' in actions:
                del actions['mark_as_in_progress_and_assign']
        return actions
    

    def has_change_permission(self, request, obj=None):
        # Permet aux superutilisateurs de tout modifier
        if request.user.is_superuser:
            return True
        
        # Pour les autres utilisateurs (agents)
        if obj is not None:
            # Si le ticket est assigné et l'utilisateur n'est PAS l'agent assigné
            if obj.agent and obj.agent != request.user:
                return False # N'autorise pas la modification
            # Si le ticket est assigné et l'utilisateur EST l'agent assigné, ou si le ticket n'est pas encore assigné
            # Dans ce cas, l'agent peut le modifier s'il est assigné ou s'il n'est pas assigné (pour le prendre en charge via l'action)
            return True 
        
        # Pour la vue de liste (si obj est None), si l'utilisateur est staff, il peut voir la liste
        # La permission de base (Can change ticket) est déjà vérifiée par Django
        return super().has_change_permission(request, obj)