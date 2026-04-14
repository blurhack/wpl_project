from django.contrib import admin

from .models import Seat


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('flight', 'code', 'cabin', 'price_modifier', 'is_blocked')
    list_filter = ('cabin', 'is_blocked', 'flight')
    search_fields = ('code', 'flight__flight_no')
