from django.urls import path
from .views import TicketSubmitAPIView, TicketListAPIView, TicketDetailAPIView 

urlpatterns = [
    path('submit/', TicketSubmitAPIView.as_view(), name='ticket-submit'),
    path('', TicketListAPIView.as_view(), name='ticket-list'), 
    path('<int:pk>/', TicketDetailAPIView.as_view(), name='ticket-detail'), 
]
