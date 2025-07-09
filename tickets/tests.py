from django.test import TestCase
from django.contrib import admin
from .models import Ticket
from .admin import TicketAdmin
from .forms import TicketAdminForm
from django.contrib.auth.models import User
from unittest.mock import Mock

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
