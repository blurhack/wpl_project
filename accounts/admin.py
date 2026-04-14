from django.contrib import admin

from .models import Passenger


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'government_id', 'created_at')
    search_fields = ('full_name', 'email', 'phone', 'government_id')
