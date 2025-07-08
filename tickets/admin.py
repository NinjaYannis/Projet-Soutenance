
from django.contrib import admin
from .models import Ticket
from django.contrib.auth.models import User # Importez le modèle User de Django (nécessaire pour agent_display si User n'est pas importé ailleurs)

@admin.register(Ticket) # Utilise le décorateur pour enregistrer le modèle
class TicketAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste des tickets
    list_display = (
        'id', 'subject', 'status', 'priority', 'platform_name',
        'first_name', 'last_name', 'email', 'submission_date', 'agent_display'
    )

    # Filtres dans la barre latérale droite
    list_filter = ('status', 'priority', 'platform_name', 'submission_date')

    # Champs de recherche
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')

    # Champs en lecture seule (non modifiables via l'admin)
    readonly_fields = ('submission_date',)

    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        (None, {
            'fields': ('subject', 'message', 'platform_name')
        }),
        ('Informations du plaignant', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Statut et Priorité', {
            'fields': ('status', 'priority', 'agent') # 'agent' est le champ FK vers l'utilisateur
        }),
        ('Dates', {
            'fields': ('submission_date',)
        }),
    )

    # Méthode personnalisée pour afficher le nom de l'agent
    # Ceci permet d'afficher le prénom et nom de l'agent au lieu de juste son ID
    def agent_display(self, obj):
        if obj.agent:
            return f"{obj.agent.first_name} {obj.agent.last_name} ({obj.agent.username})"
        return "Non assigné"
    agent_display.short_description = 'Agent Assigné' # Nom de la colonne dans l'admin