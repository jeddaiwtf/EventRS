from django.urls import path
from . import views

urlpatterns = [
    # ===== API Endpoints =====
    path("api/register/", views.RegisterTicketAPI.as_view(), name="api_register_ticket"),
    path("api/detail/<uuid:pk>/", views.TicketDetailAPI.as_view(), name="api_ticket_detail"),

    # ===== HTML Pages =====
    path("register/", views.register_ticket, name="ticket-register-page"),
    path("landing/", views.landing_validate_page, name="landing_validate_page"),
    path("manage-events/", views.manage_events, name="manage_events"),

    # Validation URL using token from QR code
    path("validate/<str:token>/", views.validate_ticket, name="validate_ticket"),
]
