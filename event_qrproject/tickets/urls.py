# tickets/urls.py
from django.urls import path
from .views import RegisterTicketAPI, TicketDetailAPI, register_page, landing_validate_page
from .validation_views import validate_ticket_api
from . import views

urlpatterns = [
    path('register/', views.register_page, name='ticket-register-page'),
    path('landing/<uuid:ticket_id>/<str:signature>/', views.landing_validate_page, name='ticket-landing'),
    path('manage-events/', views.manage_events, name='manage-events'),
]