# tickets/tests.py
from django.test import TestCase
from django.contrib import admin
from .models import Ticket
from .admin import TicketAdmin # Importez votre classe TicketAdmin
from django.contrib.auth.models import User
from unittest.mock import Mock # Pour mocker l'objet request

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

#   def test_readonly_fields_configuration(self):
#       """
#       Vérifie que les champs en lecture seule sont correctement définis.
#       """
#       expected_readonly_fields = ('submission_date',)
#       self.assertEqual(TicketAdmin.readonly_fields, expected_readonly_fields)

    # Vous pouvez ajouter d'autres tests pour fieldsets si vous le souhaitez,


class TicketAdminLogicTest(TestCase):
    def setUp(self):
        # Crée un superutilisateur et un agent pour les tests
        self.superuser = User.objects.create_superuser('admin_test', 'admin@example.com', 'adminpass')
        self.agent = User.objects.create_user('agent_test', 'agent@example.com', 'agentpass')
        self.agent.is_staff = True
        self.agent.save()

        # Crée un ticket 'nouveau'
        self.new_ticket = Ticket.objects.create(
            first_name="Test", last_name="User", email="test@example.com",
            subject="Problème de test", message="Ceci est un message de test.",
            platform_name="TestPlatform", status="nouveau", priority="basse"
        )

    def test_agent_cannot_modify_protected_fields(self):
        """
        Vérifie que les champs protégés sont en lecture seule pour un agent non-superuser.
        """
        request = Mock()
        request.user = self.agent
        admin_instance = TicketAdmin(Ticket, admin.site)

        readonly_fields = admin_instance.get_readonly_fields(request, self.new_ticket)
        expected_readonly_for_agent = (
            'first_name', 'last_name', 'email', 'platform_name',
            'submission_date', 'subject', 'message'
        )
        self.assertEqual(set(readonly_fields), set(expected_readonly_for_agent))

    def test_superuser_can_modify_all_fields_except_submission_date(self):
        """
        Vérifie qu'un superutilisateur peut modifier tous les champs sauf la date de soumission.
        """
        request = Mock()
        request.user = self.superuser
        admin_instance = TicketAdmin(Ticket, admin.site)

        readonly_fields = admin_instance.get_readonly_fields(request, self.new_ticket)
        self.assertEqual(readonly_fields, ('submission_date',))

    def test_agent_assignation_on_status_change_from_new_to_in_progress(self):
        """
        Vérifie que l'agent est automatiquement assigné lorsque le statut passe de 'nouveau' à 'en cours de traitement'.
        """
        request = Mock()
        request.user = self.agent # L'agent qui fait la modification

        ticket_instance = self.new_ticket # Le ticket original

        # Simule le formulaire, avec le statut initial et le nouveau statut
        form = Mock()
        form.initial = {'status': 'nouveau'} # Statut avant la modification

        ticket_instance.status = 'en cours de traitement' # Nouveau statut

        admin_instance = TicketAdmin(Ticket, admin.site)
        admin_instance.save_model(request, ticket_instance, form, True) # True pour 'change'

        self.assertEqual(ticket_instance.agent, self.agent)
        self.assertEqual(ticket_instance.status, 'en cours de traitement')

    def test_agent_not_assigned_if_already_assigned(self):
        """
        Vérifie que l'agent n'est pas réassigné si le ticket a déjà un agent.
        """
        other_agent = User.objects.create_user('other_agent', 'other@example.com', 'otherpass')
        other_agent.is_staff = True
        other_agent.save()

        self.new_ticket.agent = other_agent # Ticket déjà assigné
        self.new_ticket.save()

        request = Mock()
        request.user = self.agent # Un autre agent essaie de le prendre

        form = Mock()
        form.initial = {'status': 'nouveau'}

        self.new_ticket.status = 'en cours de traitement' # Tente de changer le statut

        admin_instance = TicketAdmin(Ticket, admin.site)
        admin_instance.save_model(request, self.new_ticket, form, True)

        # L'agent ne devrait PAS avoir changé
        self.assertEqual(self.new_ticket.agent, other_agent)
        self.assertEqual(self.new_ticket.status, 'en cours de traitement')
