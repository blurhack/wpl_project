from django.contrib import admin

from seats.models import Seat

from .models import Aircraft, Flight


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0
    fields = ('code', 'cabin', 'price_modifier', 'is_blocked')


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('tail_number', 'manufacturer', 'model', 'capacity', 'rows', 'seats_per_row')
    search_fields = ('tail_number', 'model', 'manufacturer')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_no', 'airline', 'origin', 'destination', 'depart_at', 'status', 'seats_left', 'dynamic_price')
    list_filter = ('status', 'origin', 'destination', 'airline')
    search_fields = ('flight_no', 'airline', 'origin', 'destination')
    inlines = [SeatInline]
