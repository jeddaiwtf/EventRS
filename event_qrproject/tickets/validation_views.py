# tickets/validation_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Ticket
from .utils import verify_signature

@api_view(["POST"])
@permission_classes([AllowAny])
def validate_ticket_api(request):
    payload = request.data.get("payload")
    if payload and "|" in payload:
        ticket_id, sig = payload.split("|", 1)
    else:
        ticket_id = request.data.get("ticket_id")
        sig = request.data.get("signature")

    if not ticket_id or not sig:
        return Response({"status": "error", "reason": "invalid_payload"}, status=status.HTTP_400_BAD_REQUEST)

    if not verify_signature(ticket_id, sig):
        return Response({"status": "error", "reason": "invalid_signature"}, status=status.HTTP_403_FORBIDDEN)

    ticket = get_object_or_404(Ticket, pk=ticket_id)

    if ticket.status == Ticket.STATUS_USED:
        return Response({"status": "error", "reason": "already_used", "used_at": ticket.used_at}, status=status.HTTP_409_CONFLICT)

    # mark used
    ticket.status = Ticket.STATUS_USED
    ticket.used_at = timezone.now()
    ticket.save()

    return Response({"status": "ok", "ticket_id": str(ticket.id), "used_at": ticket.used_at}, status=status.HTTP_200_OK)
