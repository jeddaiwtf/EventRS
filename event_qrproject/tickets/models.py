import uuid
from django.db import models
from django.utils import timezone


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_at <= now <= self.end_at

    @property
    def is_expired(self):
        return timezone.now() > self.end_at


class Ticket(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("used", "Used"),
        ("expired", "Expired"),
        ("invalid", "Invalid"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)
    qr_image = models.ImageField(upload_to="tickets/qr_codes/", blank=True, null=True)
    signature = models.CharField(max_length=255, blank=True, null=True)
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Ticket for {self.event.title}"

    # ✅ Core validation logic
    def mark_as_used(self):
        """
        Mark the ticket as used, or return status message if expired/used.
        Returns tuple: (success: bool, message: str)
        """
        now = timezone.now()

        if self.event.end_at < now:
            self.status = "expired"
            self.save()
            return False, "This ticket is expired. The event has ended."

        if self.status == "used":
            return False, f"This ticket was already validated at {self.used_at.strftime('%Y-%m-%d %H:%M:%S')}."

        self.status = "used"
        self.used_at = now
        self.save()
        return True, "Ticket successfully validated!"
