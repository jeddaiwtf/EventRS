from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket, Event

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "status", "signature", "created_at")
    readonly_fields = ('qr_image_preview',)  # add other readonly fields as needed

    def qr_image_preview(self, obj):
        url = getattr(obj, 'qr_image_url', None)
        if not url:
            return "(no QR)"
        return format_html('<a href="{0}" target="_blank">{0}</a><br><img src="{0}" style="max-width:200px;max-height:200px;" />', url)
    qr_image_preview.short_description = "QR image / URL"

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_at", "end_at")
