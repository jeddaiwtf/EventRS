import io
import qrcode
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from .models import Ticket, Event
from .serializers import TicketRegisterSerializer, TicketResponseSerializer
from datetime import datetime
from django.utils import timezone
from django.contrib import messages


# =============================
# API VIEWS
# =============================
class RegisterTicketAPI(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        serializer = TicketRegisterSerializer(data=request.data)
        if serializer.is_valid():
            event_id = serializer.validated_data["event_id"]
            event = get_object_or_404(Event, id=event_id)

            ticket = Ticket.objects.create(event=event)

            # Use token for secure QR link
            base_url = getattr(settings, "BASE_URL", "http://127.0.0.1:8000")
            qr_url = f"{base_url}/tickets/validate/{ticket.token}/"
            qr_image = qrcode.make(qr_url)
            buffer = io.BytesIO()
            qr_image.save(buffer, format="PNG")
            ticket.qr_image.save(f"ticket_{ticket.id}.png", ContentFile(buffer.getvalue()), save=True)

            response_serializer = TicketResponseSerializer(ticket)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketDetailAPI(APIView):
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        serializer = TicketResponseSerializer(ticket)
        return Response(serializer.data)


# =============================
# HTML VIEWS
# =============================
def register_ticket(request):
    if request.method == "POST":
        event_id = request.POST.get("event_id")

        if not event_id:
            return render(request, "tickets/register.html", {
                "events": Event.objects.all(),
                "error": "Please select an event.",
            })

        event = get_object_or_404(Event, id=event_id)
        ticket = Ticket.objects.create(event=event)

        base_url = getattr(settings, "BASE_URL", "http://127.0.0.1:8000")
        qr_url = f"{base_url}/tickets/validate/{ticket.token}/"
        qr_image = qrcode.make(qr_url)
        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        ticket.qr_image.save(f"ticket_{ticket.id}.png", ContentFile(buffer.getvalue()), save=True)

        return render(request, "tickets/register.html", {
            "success": True,
            "ticket": ticket,
            "qr_url": ticket.qr_image.url if ticket.qr_image else None,
            "fallback": qr_url,
        })

    events = Event.objects.all()
    return render(request, "tickets/register.html", {"events": events})


def validate_ticket(request, token):
    """Validate ticket when QR code is scanned."""
    ticket = get_object_or_404(Ticket, token=token)

    success, message = ticket.mark_as_used()
    color = "success" if success else "danger" if ticket.status == "used" else "secondary"

    return render(request, "tickets/validate.html", {
        "ticket": ticket,
        "message": message,
        "color": color
    })


def landing_validate_page(request):
    return render(request, "tickets/landing_validate.html")


def manage_events(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        location = request.POST.get("location")
        start_at_str = request.POST.get("start_at")
        end_at_str = request.POST.get("end_at")

        if title and start_at_str and end_at_str:
            try:
                start_at = timezone.make_aware(datetime.fromisoformat(start_at_str))
                end_at = timezone.make_aware(datetime.fromisoformat(end_at_str))
                Event.objects.create(
                    title=title,
                    description=description,
                    location=location,
                    start_at=start_at,
                    end_at=end_at,
                )
                messages.success(request, f"✅ Event '{title}' created successfully.")
                return redirect("manage_events")

            except Exception as e:
                messages.error(request, f"⚠️ Failed to create event: {e}")
        else:
            messages.error(request, "Please fill out all required fields.")

    events = Event.objects.all().order_by("-start_at")
    return render(request, "tickets/manage_events.html", {"events": events})
