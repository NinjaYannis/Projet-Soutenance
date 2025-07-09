# tickets/forms.py
from django import forms
from .models import Ticket
from django.contrib.auth.models import User # Pour les vérifications d'utilisateur dans le formulaire

class TicketAdminForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = '__all__' # Utiliser tous les champs par défaut

    def __init__(self, *args, **kwargs):
        # Récupérer l'objet request avant d'appeler super().__init__
        self.request = kwargs.pop('request', None) # Récupère 'request' si passé, et le retire des kwargs
        super().__init__(*args, **kwargs)
        
        # S'assurer que le champ 'status' existe dans self.fields avant de tenter de le modifier
        if 'status' in self.fields: # <-- AJOUTEZ CETTE VÉRIFICATION
            # Si nous éditons un objet existant
            if self.instance.pk:
                # Recharge l'objet depuis la base de données pour avoir le statut le plus à jour
                self.instance.refresh_from_db()
                current_status = self.instance.status
            else:
                # Pour un nouvel objet, le statut initial est 'nouveau'
                current_status = 'nouveau'
            
            # Applique la logique de choix pour les agents
            # Vérifiez si request est disponible et si l'utilisateur n'est pas un superutilisateur
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
                else: # Fallback pour un statut inattendu ou si l'objet est nouveau
                    self.fields['status'].choices = [(current_status, dict(Ticket.STATUS_CHOICES).get(current_status, current_status))]
            # else: Si c'est un superutilisateur ou pas de request (ex: en dehors de l'admin),
            # les choix restent ceux par défaut du modèle (tous les STATUS_CHOICES)