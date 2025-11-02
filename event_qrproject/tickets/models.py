import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-start_at",)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    STATUS_UNUSED = "unused"
    STATUS_USED = "used"
    STATUS_CHOICES = [
        (STATUS_UNUSED, "Unused"),
        (STATUS_USED, "Used"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets", null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UNUSED)
    used_at = models.DateTimeField(null=True, blank=True)
    qr_code_url = models.URLField(blank=True, null=True)
    signature = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Ticket {self.id} ({self.status})"
