from rest_framework import serializers
from .models import Ticket, Event

class TicketRegisterSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()

class TicketResponseSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source="event.title", read_only=True)
    class Meta:
        model = Ticket
        fields = ("id", "event", "event_title", "status", "created_at", "used_at", "qr_image", "signature")
        read_only_fields = fields
