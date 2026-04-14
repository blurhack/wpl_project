import random
import string
from decimal import Decimal

from django.db import models


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

    class Meta:
        ordering = ['code']

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
    passenger = models.ForeignKey('accounts.Passenger', related_name='bookings', on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    flight = models.ForeignKey('flights.Flight', related_name='bookings', on_delete=models.CASCADE)
    seat = models.ForeignKey('seats.Seat', related_name='bookings', on_delete=models.PROTECT)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    booking_mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='USER')
    agent = models.ForeignKey('agents.Agent', null=True, blank=True, related_name='bookings', on_delete=models.SET_NULL)
    agent_name = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
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


class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    ]

    booking = models.OneToOneField(Booking, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    method = models.CharField(max_length=40, default='Lab Demo Payment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PAID')
    transaction_id = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.booking.pnr} · {self.status}'
