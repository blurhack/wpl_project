import random
import string
from decimal import Decimal

from django.db import models
from django.utils import timezone


class Flight(models.Model):
    STATUS_CHOICES = [
        ('CHECKIN', 'Check-in Open'),
        ('ON_TIME', 'On Time'),
        ('BOARDING', 'Boarding'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    ]

    flight_no = models.CharField(max_length=12, unique=True)
    airline = models.CharField(max_length=80)
    origin = models.CharField(max_length=80)
    destination = models.CharField(max_length=80)
    depart_at = models.DateTimeField()
    arrive_at = models.DateTimeField()
    base_price = models.DecimalField(max_digits=9, decimal_places=2)
    seats_total = models.PositiveIntegerField(default=60)
    gate = models.CharField(max_length=10, default='A1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ON_TIME')
    delay_minutes = models.PositiveIntegerField(default=0)
    checkin_open = models.BooleanField(default=True)
    document_check_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['depart_at']

    def __str__(self):
        return f'{self.flight_no} {self.origin} to {self.destination}'

    @property
    def seats_booked(self):
        return self.bookings.filter(status='CONFIRMED').count()

    @property
    def seats_left(self):
        return max(self.seats_total - self.seats_booked, 0)

    @property
    def dynamic_price(self):
        demand = Decimal(self.seats_booked) / Decimal(max(self.seats_total, 1))
        multiplier = Decimal('1.00') + (demand * Decimal('0.45'))
        hours_left = max((self.depart_at - timezone.now()).total_seconds() / 3600, 0)
        if hours_left < 24:
            multiplier += Decimal('0.18')
        elif hours_left < 72:
            multiplier += Decimal('0.10')
        return (self.base_price * multiplier).quantize(Decimal('1'))

    @property
    def delay_support(self):
        if self.delay_minutes >= 180:
            return 'Hotel desk + meal voucher + free reschedule window active'
        if self.delay_minutes >= 90:
            return 'Meal voucher + priority rebooking support active'
        if self.delay_minutes > 0:
            return 'Delay alert sent with updated gate and time'
        return 'No accommodation needed'


class Seat(models.Model):
    CABIN_CHOICES = [
        ('Economy', 'Economy'),
        ('Premium', 'Premium'),
        ('Business', 'Business'),
    ]

    flight = models.ForeignKey(Flight, related_name='seats', on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    cabin = models.CharField(max_length=20, choices=CABIN_CHOICES, default='Economy')
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['flight', 'code']
        ordering = ['code']

    def __str__(self):
        return f'{self.flight.flight_no} {self.code}'


class Coupon(models.Model):
    DISCOUNT_CHOICES = [
        ('PERCENT', 'Percent'),
        ('FLAT', 'Flat'),
    ]

    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=140)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_CHOICES)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def apply(self, amount):
        if not self.active:
            return amount
        if self.discount_type == 'PERCENT':
            discount = amount * (self.value / Decimal('100'))
        else:
            discount = self.value
        return max(amount - discount, Decimal('0')).quantize(Decimal('1'))


class Booking(models.Model):
    MODE_CHOICES = [
        ('USER', 'Passenger Booking'),
        ('AGENT', 'Agent Booking'),
    ]
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    DOCUMENT_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUBMITTED', 'Submitted'),
        ('CLEARED', 'Cleared'),
    ]

    pnr = models.CharField(max_length=8, unique=True, blank=True)
    passenger_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    flight = models.ForeignKey(Flight, related_name='bookings', on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, related_name='bookings', on_delete=models.PROTECT)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    booking_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='USER')
    agent_name = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    document_status = models.CharField(max_length=20, choices=DOCUMENT_CHOICES, default='PENDING')
    checked_in = models.BooleanField(default=False)
    accommodation_note = models.CharField(max_length=180, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pnr:
            alphabet = string.ascii_uppercase + string.digits
            while True:
                code = ''.join(random.choice(alphabet) for _ in range(6))
                if not Booking.objects.filter(pnr=code).exists():
                    self.pnr = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.pnr} - {self.passenger_name}'
