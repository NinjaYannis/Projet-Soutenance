from django.contrib import admin
from django.contrib import messages
from .models import Ticket
from django.contrib.auth.models import User
from .forms import TicketAdminForm


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'subject', 'status', 'priority', 'platform_name',
        'first_name', 'last_name', 'email', 'submission_date', 'agent_display'
    )
    list_filter = ('status', 'priority', 'platform_name', 'submission_date')
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')

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

    form = TicketAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def agent_display(self, obj):
        if obj.agent:
            return f"{obj.agent.first_name} {obj.agent.last_name} ({obj.agent.username})"
        return "Non assigné"
    agent_display.short_description = 'Agent Assigné'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ('submission_date',)
        else:
            return (
                'first_name', 'last_name', 'email', 'platform_name',
                'submission_date', 'subject', 'message'
            )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    actions = ['mark_as_in_progress_and_assign']

    def mark_as_in_progress_and_assign(self, request, queryset):
        tickets_to_update = queryset.filter(status='nouveau', agent__isnull=True)
        updated_count = 0
        for ticket in tickets_to_update:
            ticket.status = 'en cours de traitement'
            ticket.agent = request.user
            ticket.save()
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
        if request.user.is_superuser:
            return True
        
        if obj is not None:
            if obj.agent and obj.agent != request.user:
                return False
            return True
        
        return super().has_change_permission(request, obj)
