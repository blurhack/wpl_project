from django.contrib import admin

from .models import DelayAlert


@admin.register(DelayAlert)
class DelayAlertAdmin(admin.ModelAdmin):
    list_display = ('flight', 'delay_minutes', 'reason', 'accommodation_type', 'active', 'created_at')
    list_filter = ('accommodation_type', 'active')
    search_fields = ('flight__flight_no', 'reason', 'message')
