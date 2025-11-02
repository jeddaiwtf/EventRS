from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib import messages
from datetime import datetime
from .models import Ticket, Event
from .serializers import TicketRegisterSerializer, TicketResponseSerializer
from .utils import make_signature, build_payload, verify_signature  # removed generate_qr_and_save

import urllib.parse


# -------------------------
# Helper function – External QR via GoQR API
# -------------------------
def generate_external_qr_url(data):
    """
    Generates a QR code URL using the free GoQR API.
    """
    base_url = "https://api.qrserver.com/v1/create-qr-code/"
    encoded_data = urllib.parse.quote_plus(data)
    qr_url = f"{base_url}?data={encoded_data}&size=300x300"
    return qr_url


# -------------------------
# API Views (Register & detail)
# -------------------------
class RegisterTicketAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = TicketRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event_id = serializer.validated_data["event_id"]
        event = get_object_or_404(Event, pk=event_id)

        ticket = Ticket.objects.create(
            event=event,
            owner=request.user if request.user.is_authenticated else None
        )

        # Create signature and payload
        sig = make_signature(str(ticket.id))
        payload = build_payload(str(ticket.id), sig)

        # External QR API call
        try:
            qr_url = generate_external_qr_url(payload)
            ticket.signature = sig
            ticket.qr_image_url = qr_url  # assuming you updated the model to use URLField
            ticket.save()

            return Response({
                "ticket_id": str(ticket.id),
                "qr_url": qr_url,
                "signature": sig
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            ticket.signature = sig
            ticket.save()
            return Response({
                "ticket_id": str(ticket.id),
                "payload": payload,
                "warning": "qr_api_failed",
                "detail": str(e)
            }, status=status.HTTP_201_CREATED)


class TicketDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, ticket_id, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        if ticket.owner and ticket.owner != request.user and not request.user.is_staff:
            return Response({"detail": "forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = TicketResponseSerializer(ticket)
        data = serializer.data
        if hasattr(ticket, 'qr_image_url') and ticket.qr_image_url:
            data['qr_url'] = ticket.qr_image_url
        return Response(data)


# -------------------------
# Web Views (register page & organizer landing)
# -------------------------
def register_page(request):
    """
    Web registration form.
    On submit: create Ticket, generate signature, create a QR code image URL using GoQR API.
    """
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        event_pk = request.POST.get("event_id")

        # Retrieve event if selected
        event = Event.objects.filter(pk=event_pk).first() if event_pk else None

        ticket = Ticket.objects.create(event=event)

        # Generate signature and full landing URL
        sig = make_signature(str(ticket.id))
        landing_path = reverse("ticket-landing", args=[str(ticket.id), sig])
        landing_full = request.build_absolute_uri(landing_path)

        # Build external QR code URL
        try:
            qr_url = generate_external_qr_url(landing_full)
            ticket.signature = sig
            ticket.qr_image_url = qr_url
            ticket.save()
        except Exception as e:
            ticket.signature = sig
            ticket.save()
            qr_url = None

        events = Event.objects.all().order_by("-start_at")[:20]
        return render(request, "tickets/register.html", {
            "success": True,
            "ticket": ticket,
            "qr_url": ticket.qr_image_url if ticket.qr_image_url else qr_url,
            "fallback": landing_full if not qr_url else None,
            "events": events
        })

    # GET: show form
    events = Event.objects.all().order_by("-start_at")[:20]
    return render(request, "tickets/register.html", {"events": events})


def landing_validate_page(request, ticket_id, signature):
    """
    Organizer landing page: verifies signature for ticket_id and signature arg.
    If valid and unused -> mark used and show success. If invalid -> show invalid.
    URL pattern: /tickets/landing/<ticket_id>/<signature>/
    """
    # Verify signature
    try:
        is_sig_valid = verify_signature(ticket_id, signature)
    except Exception:
        is_sig_valid = False

    if not is_sig_valid:
        return render(request, "tickets/validate_ticket.html", {"valid": False, "reason": "invalid_signature"})

    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return render(request, "tickets/validate_ticket.html", {"valid": False, "reason": "not_found"})

    # Check if already used
    if ticket.status == Ticket.STATUS_USED:
        return render(request, "tickets/validate_ticket.html", {"valid": False, "reason": "already_used", "ticket": ticket})

    # Check if event expired
    now = timezone.now()
    if ticket.event and ticket.event.end_at and now > ticket.event.end_at:
        return render(request, "tickets/validate_ticket.html", {"valid": False, "reason": "event_expired", "ticket": ticket})

    # Mark used
    ticket.status = Ticket.STATUS_USED
    ticket.used_at = timezone.now()
    ticket.save()

    return render(request, "tickets/validate_ticket.html", {"valid": True, "ticket": ticket})

def manage_events(request):
    """
    Interactive page for admins to create and view events
    """
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        start_at_str = request.POST.get("start_at")
        end_at_str = request.POST.get("end_at")

        # ✅ Convert to datetime objects
        try:
            start_at = datetime.fromisoformat(start_at_str)
            end_at = datetime.fromisoformat(end_at_str)
        except Exception:
            messages.error(request, "⚠️ Invalid date format.")
            return redirect("manage-events")

        if title and start_at and end_at:
            Event.objects.create(
                title=title,
                description=description,
                location=location,
                start_at=start_at,
                end_at=end_at
            )
            messages.success(request, "✅ Event created successfully!")
            return redirect("manage-events")
        else:
            messages.error(request, "⚠️ Please fill all required fields.")

    events = Event.objects.all().order_by("-start_at")
    return render(request, "tickets/manage_events.html", {"events": events})