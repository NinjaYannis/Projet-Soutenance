from django import forms
from .models import Ticket
from django.contrib.auth.models import User

class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if 'status' in self.fields:
            if self.instance.pk:
                self.instance.refresh_from_db()
                current_status = self.instance.status
            else:
                current_status = 'nouveau'
            
            if self.request and not self.request.user.is_superuser: 
                if current_status == 'nouveau':
                    self.fields['status'].choices = [
                        ('nouveau', 'Nouveau'),
                        ('en cours de traitement', 'En cours de traitement'),
                        ('ignore', 'Ignoré'),
                    ]
                elif current_status == 'en cours de traitement':
                    self.fields['status'].choices = [
                        ('en cours de traitement', 'En cours de traitement'),
                        ('resolu', 'Résolu'), 
                        ('ignore', 'Ignoré'),
                    ]
                elif current_status in ['resolu', 'ignore']:
                    self.fields['status'].choices = [(current_status, dict(Ticket.STATUS_CHOICES).get(current_status, current_status))]
                else: 
                    self.fields['status'].choices = [(current_status, dict(Ticket.STATUS_CHOICES).get(current_status, current_status))]