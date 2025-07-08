from django.urls import path
from .views import TicketSubmitAPIView

urlpatterns = [
    path('submit/', TicketSubmitAPIView.as_view(), name='ticket-submit'),
]