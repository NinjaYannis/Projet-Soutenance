# tickets/models.py
from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    # Définition des choix pour le statut du ticket
    STATUS_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en cours de traitement', 'En cours de traitement'),
        ('resolu', 'Résolu'), # Utilisons 'resolu' comme valeur interne, 'Achevé' comme libellé si c'est la même chose
        ('ignore', 'Ignoré'),
    ]

    # L'ID primaire (ticket_id) est géré automatiquement par Django comme 'id' par défaut.
    # Si vous voulez explicitement qu'il s'appelle 'ticket_id' et soit BIGINT,
    # vous pouvez utiliser: ticket_id = models.BigAutoField(primary_key=True)
    # Sinon, Django créera un 'id' de type BIGINT par défaut sur PostgreSQL.
    # Pour la simplicité et la compatibilité Django, nous nous baserons sur 'id'.

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    submission_date = models.DateTimeField(default=timezone.now)
    platform_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='nouveau') # Utilise les choix
    priority = models.CharField(max_length=50, default='basse')


     #Clé étrangère vers l'agent qui traite le ticket.
    # 'auth.User' fait référence au modèle utilisateur par défaut de Django.
    # on_delete=models.SET_NULL signifie que si un agent est supprimé, son 'agent_id' devient NULL sur les tickets qu'il traitait.
    # null=True et blank=True permettent que ce champ soit vide (NULL en BDD) si un ticket n'est pas encore assigné.
    agent = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets' # Nom pour la relation inverse (agent.assigned_tickets
    )

    # Classe Meta pour les options du modèle
    class Meta:
        verbose_name = "Ticket de plainte" # Nom affiché dans l'admin Django (singulier)
        verbose_name_plural = "Tickets de plainte" # Nom affiché dans l'admin Django (pluriel)
        ordering = ['-submission_date'] # Ordonne les tickets par date de soumission décroissante par défaut


    # Méthode __str__ pour une représentation lisible de l'objet
    def __str__(self):
        return f"Ticket {self.id}: {self.subject} ({self.status})"