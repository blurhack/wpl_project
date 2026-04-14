from django.contrib import admin

from .models import CheckEvent


@admin.register(CheckEvent)
class CheckEventAdmin(admin.ModelAdmin):
    list_display = ('booking', 'event_type', 'status', 'note', 'created_at')
    list_filter = ('event_type', 'status')
    search_fields = ('booking__pnr', 'note')
