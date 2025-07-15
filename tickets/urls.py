from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketSubmitAPIView, TicketViewSet

router = DefaultRouter()
router.register(r'', TicketViewSet)  # Ça va gérer /api/tickets/

urlpatterns = [
    path('submit/', TicketSubmitAPIView.as_view(), name='ticket-submit'),
    path('', include(router.urls)),
]