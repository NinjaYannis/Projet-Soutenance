from django.urls import path
from .views import TicketSubmitAPIView, TicketListAPIView, TicketDetailAPIView, TicketUpdateAPIView

urlpatterns = [
    path('submit/', TicketSubmitAPIView.as_view(), name='ticket-submit'),
    path('', TicketListAPIView.as_view(), name='ticket-list'),
    path('<int:pk>/', TicketDetailAPIView.as_view(), name='ticket-detail'),
    path('<int:pk>/update/', TicketUpdateAPIView.as_view(), name='ticket-update'),
]