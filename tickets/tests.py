from django.test import TestCase
from django.contrib import admin
from .models import Ticket
from .admin import TicketAdmin
from .forms import TicketAdminForm
from django.contrib.auth.models import User
from unittest.mock import Mock
from django.test import TestCase
from django.contrib import admin
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from django.db.models import Q 
from rest_framework import status



class TicketAdminTest(TestCase):
    def test_ticket_model_registered_with_admin(self):
        self.assertIn(Ticket, admin.site._registry)
        self.assertIsInstance(admin.site._registry[Ticket], TicketAdmin)

    def test_list_display_configuration(self):
        expected_list_display = (
            'id', 'subject', 'status', 'priority', 'platform_name',
            'first_name', 'last_name', 'email', 'submission_date', 'agent_display'
        )
        self.assertEqual(TicketAdmin.list_display, expected_list_display)

    def test_list_filter_configuration(self):
        expected_list_filter = ('status', 'priority', 'platform_name', 'submission_date')
        self.assertEqual(TicketAdmin.list_filter, expected_list_filter)

    def test_search_fields_configuration(self):
        expected_search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
        self.assertEqual(TicketAdmin.search_fields, expected_search_fields)

class TicketAdminLogicTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin_test', 'admin@example.com', 'adminpass')
        self.agent = User.objects.create_user('agent_test', 'agent@example.com', 'agentpass')
        self.agent.is_staff = True
        self.agent.save()

        self.new_ticket = Ticket.objects.create(
            first_name="Test", last_name="User", email="test@example.com",
            subject="Problème de test", message="Ceci est un message de test.",
            platform_name="TestPlatform", status="nouveau", priority="basse"
        )

        self.in_progress_ticket = Ticket.objects.create(
            first_name="Ongoing", last_name="User", email="ongoing@example.com",
            subject="Ticket en cours de traitement", message="Ceci est un message de test.",
            platform_name="TestPlatform", status="en cours de traitement", priority="moyenne",
            agent=self.agent
        )

    def test_agent_cannot_modify_protected_fields(self):
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
        request = Mock()
        request.user = self.superuser
        admin_instance = TicketAdmin(Ticket, admin.site)
        readonly_fields = admin_instance.get_readonly_fields(request, self.new_ticket)
        self.assertEqual(readonly_fields, ('submission_date',))

    def test_agent_assignation_on_status_change_via_admin_action(self):
        request = Mock()
        request.user = self.agent
        admin_instance = TicketAdmin(Ticket, admin.site)
        queryset = Ticket.objects.filter(pk=self.new_ticket.pk)
        admin_instance.mark_as_in_progress_and_assign(request, queryset)
        self.new_ticket.refresh_from_db()
        self.assertEqual(self.new_ticket.agent, self.agent)
        self.assertEqual(self.new_ticket.status, 'en cours de traitement')

    def test_agent_not_assigned_if_already_assigned_via_action(self):
        other_agent = User.objects.create_user('other_agent', 'other@example.com', 'otherpass')
        other_agent.is_staff = True
        other_agent.save()
        self.new_ticket.agent = other_agent
        self.new_ticket.save()
        request = Mock()
        request.user = self.agent
        admin_instance = TicketAdmin(Ticket, admin.site)
        queryset = Ticket.objects.filter(pk=self.new_ticket.pk)
        admin_instance.mark_as_in_progress_and_assign(request, queryset)
        self.new_ticket.refresh_from_db()
        self.assertEqual(self.new_ticket.agent, other_agent)
        self.assertEqual(self.new_ticket.status, 'nouveau')

    def test_status_choices_for_new_ticket_by_agent(self):
        request = Mock()
        request.user = self.agent
        form_instance = TicketAdminForm(instance=self.new_ticket, request=request)
        choices = form_instance.fields['status'].choices
        expected_choices = [
            ('nouveau', 'Nouveau'),
            ('en cours de traitement', 'En cours de traitement'),
            ('ignore', 'Ignoré'),
        ]
        self.assertEqual(choices, expected_choices)

    def test_status_choices_for_in_progress_ticket_by_agent(self):
        request = Mock()
        request.user = self.agent
        form_instance = TicketAdminForm(instance=self.in_progress_ticket, request=request)
        choices = form_instance.fields['status'].choices
        expected_choices = [
            ('en cours de traitement', 'En cours de traitement'),
            ('resolu', 'Résolu'),
            ('ignore', 'Ignoré'),
        ]
        self.assertEqual(choices, expected_choices)

    def test_status_choices_for_resolved_ticket_by_agent(self):
        resolved_ticket = Ticket.objects.create(
            first_name="Resolved", last_name="User", email="resolved@example.com",
            subject="Ticket résolu", message="Ceci est un message de test.",
            platform_name="TestPlatform", status="resolu", priority="basse",
            agent=self.agent
        )
        request = Mock()
        request.user = self.agent
        form_instance = TicketAdminForm(instance=resolved_ticket, request=request)
        choices = form_instance.fields['status'].choices
        expected_choices = [('resolu', 'Résolu')]
        self.assertEqual(choices, expected_choices)

    def test_status_choices_for_superuser(self):
        request = Mock()
        request.user = self.superuser
        form_instance = TicketAdminForm(instance=self.new_ticket, request=request)
        choices = form_instance.fields['status'].choices
        self.assertEqual(choices, Ticket.STATUS_CHOICES)





class TicketAPITest(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin_api', 'admin_api@example.com', 'adminpass')
        self.agent1 = User.objects.create_user('agent_api1', 'agent_api1@example.com', 'agentpass')
        self.agent1.is_staff = True
        self.agent1.save()
        self.agent2 = User.objects.create_user('agent_api2', 'agent_api2@example.com', 'agentpass')
        self.agent2.is_staff = True
        self.agent2.save()

        self.agent1_access_token = str(RefreshToken.for_user(self.agent1).access_token)
        self.agent2_access_token = str(RefreshToken.for_user(self.agent2).access_token)
        self.superuser_access_token = str(RefreshToken.for_user(self.superuser).access_token)

        self.ticket_assigned_to_agent1 = Ticket.objects.create(
            first_name="Alice", last_name="A", email="a@example.com",
            subject="Problème de connexion", message="Login issue.",
            platform_name="Site A", status="en cours de traitement", priority="critique",
            agent=self.agent1
        )
        self.ticket_assigned_to_agent2 = Ticket.objects.create(
            first_name="Bob", last_name="B", email="b@example.com",
            subject="Question sur la facture", message="Facture unclear.",
            platform_name="Site B", status="en cours de traitement", priority="basse",
            agent=self.agent2
        )
        self.ticket_unassigned = Ticket.objects.create(
            first_name="Charlie", last_name="C", email="c@example.com",
            subject="Erreur d'affichage", message="Display bug.",
            platform_name="Site A", status="nouveau", priority="moyenne"
        )
        self.ticket_resolved = Ticket.objects.create(
            first_name="David", last_name="D", email="d@example.com",
            subject="Ticket résolu", message="Solution appliquée.",
            platform_name="Site B", status="resolu", priority="basse",
            agent=self.agent1
        )

    def get_auth_headers(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}


    def test_agent_sees_only_assigned_and_unassigned_tickets_in_list(self):
        """
        Vérifie qu'un agent ne voit que les tickets qui lui sont assignés ou qui sont non assignés.
        """
        headers = self.get_auth_headers(self.agent1_access_token)
        response = self.client.get(reverse('ticket-list'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
 
        visible_ticket_ids = {ticket['id'] for ticket in response.data}
        expected_ticket_ids = {
            self.ticket_assigned_to_agent1.id,
            self.ticket_unassigned.id,
            self.ticket_resolved.id 
        }
        
        self.assertEqual(len(visible_ticket_ids), 3)
        self.assertEqual(visible_ticket_ids, expected_ticket_ids)
        self.assertNotIn(self.ticket_assigned_to_agent2.id, visible_ticket_ids)


    def test_agent_cannot_see_other_agents_assigned_tickets_detail(self):
        
        headers = self.get_auth_headers(self.agent1_access_token)
        response = self.client.get(reverse('ticket-detail', args=[self.ticket_assigned_to_agent2.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 

    def test_agent_can_see_their_assigned_ticket_detail(self):
        headers = self.get_auth_headers(self.agent1_access_token)
        response = self.client.get(reverse('ticket-detail', args=[self.ticket_assigned_to_agent1.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ticket_assigned_to_agent1.id)
    
    def test_agent_can_see_unassigned_ticket_detail(self):
        headers = self.get_auth_headers(self.agent1_access_token)
        response = self.client.get(reverse('ticket-detail', args=[self.ticket_unassigned.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ticket_unassigned.id)

    def test_superuser_sees_all_tickets_in_list(self):
        headers = self.get_auth_headers(self.superuser_access_token)
        response = self.client.get(reverse('ticket-list'), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_superuser_sees_all_tickets_detail(self):
        headers = self.get_auth_headers(self.superuser_access_token)
        response = self.client.get(reverse('ticket-detail', args=[self.ticket_assigned_to_agent2.id]), **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ticket_assigned_to_agent2.id)