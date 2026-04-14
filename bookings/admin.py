from django.contrib import admin

from .models import Booking, Coupon, Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'passenger_name', 'flight', 'seat', 'booking_mode', 'agent_name', 'total_amount', 'document_status', 'checked_in')
    search_fields = ('pnr', 'passenger_name', 'email', 'phone')
    list_filter = ('booking_mode', 'status', 'document_status', 'checked_in')
    inlines = [PaymentInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'discount_type', 'value', 'active')
    list_filter = ('active', 'discount_type')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'method', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('booking__pnr', 'transaction_id')
