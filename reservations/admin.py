from django.contrib import admin

from .models import Booking, Coupon, Flight, Seat


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_no', 'airline', 'origin', 'destination', 'depart_at', 'status', 'seats_left')
    list_filter = ('status', 'origin', 'destination')
    search_fields = ('flight_no', 'airline', 'origin', 'destination')
    inlines = [SeatInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'passenger_name', 'flight', 'seat', 'booking_mode', 'total_amount', 'checked_in')
    search_fields = ('pnr', 'passenger_name', 'email', 'phone')
    list_filter = ('booking_mode', 'status', 'document_status', 'checked_in')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'discount_type', 'value', 'active')
    list_filter = ('active', 'discount_type')
