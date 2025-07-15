from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('en cours de traitement', 'En cours de traitement'),
        ('resolu', 'Résolu'),
        ('ignore', 'Ignoré'),
    ]

    PRIORITY_CHOICES = [
        ('basse', 'Basse'),
        ('moyenne', 'Moyenne'),
        ('critique', 'Critique'),
    ]
    #---------------------
    first_name = models.CharField(max_length=100, verbose_name="Prénom du plaignant")
    last_name = models.CharField(max_length=100, verbose_name="Nom du plaignant")
    email = models.EmailField(max_length=255, verbose_name="Email du plaignant")
    
    subject = models.CharField(max_length=100, verbose_name="Sujet du ticket")
    message = models.TextField(verbose_name="Description détaillée")
    #---------------------
    submission_date = models.DateTimeField(default=timezone.now, verbose_name="Date de soumission")
    platform_name = models.CharField(max_length=100, verbose_name="Plateforme d'origine")
    #---------------------
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='nouveau',
        verbose_name="Statut"
    )
    
    priority = models.CharField(
        max_length=50,
        choices=PRIORITY_CHOICES,
        default='basse',
        verbose_name="Priorité"
    )

    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name="Agent assigné"
    )

    class Meta:
        verbose_name = "Ticket de plainte"
        verbose_name_plural = "Tickets de plainte"
        ordering = ['-submission_date']

    def __str__(self):
        return f"Ticket {self.id}: {self.subject} ({self.get_status_display()})"