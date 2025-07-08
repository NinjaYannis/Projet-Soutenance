# tickets/tests.py
from django.test import TestCase
from django.contrib import admin
from .models import Ticket
from .admin import TicketAdmin # Importez votre classe TicketAdmin

class TicketAdminTest(TestCase):
    def test_ticket_model_registered_with_admin(self):
        """
        Vérifie que le modèle Ticket est bien enregistré dans l'administration Django.
        """
        self.assertIn(Ticket, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Ticket], TicketAdmin)

    def test_list_display_configuration(self):
        """
        Vérifie que les champs configurés dans list_display sont corrects.
        """
        expected_list_display = (
            'id', 'subject', 'status', 'priority', 'platform_name',
            'first_name', 'last_name', 'email', 'submission_date', 'agent_display'
        )
        self.assertEqual(TicketAdmin.list_display, expected_list_display)

    def test_list_filter_configuration(self):
        """
        Vérifie que les filtres configurés dans list_filter sont corrects.
        """
        expected_list_filter = ('status', 'priority', 'platform_name', 'submission_date')
        self.assertEqual(TicketAdmin.list_filter, expected_list_filter)

    def test_search_fields_configuration(self):
        """
        Vérifie que les champs de recherche configurés dans search_fields sont corrects.
        """
        expected_search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
        self.assertEqual(TicketAdmin.search_fields, expected_search_fields)

    def test_readonly_fields_configuration(self):
        """
        Vérifie que les champs en lecture seule sont correctement définis.
        """
        expected_readonly_fields = ('submission_date',)
        self.assertEqual(TicketAdmin.readonly_fields, expected_readonly_fields)

    # Vous pouvez ajouter d'autres tests pour fieldsets si vous le souhaitez,
    # mais ceux-ci sont un bon début pour la configuration de l'admin.