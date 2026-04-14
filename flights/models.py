from decimal import Decimal

from django.db import models
from django.utils import timezone


class City(models.Model):
    name = models.CharField(max_length=80, unique=True)
    airport_code = models.CharField(max_length=6, unique=True)
    airport_name = models.CharField(max_length=120)
    country = models.CharField(max_length=80, default='India')
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cities'

    def __str__(self):
        return f'{self.name} ({self.airport_code})'


class Aircraft(models.Model):
    tail_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=80)
    manufacturer = models.CharField(max_length=80, default='Airbus')
    capacity = models.PositiveIntegerField(default=60)
    rows = models.PositiveIntegerField(default=10)
    seats_per_row = models.PositiveIntegerField(default=6)

    class Meta:
        ordering = ['tail_number']

    def __str__(self):
        return f'{self.tail_number} · {self.model}'


class Flight(models.Model):
    STATUS_CHOICES = [
        ('CHECKIN', 'Check-in Open'),
        ('ON_TIME', 'On Time'),
        ('BOARDING', 'Boarding'),
        ('DELAYED', 'Delayed'),
        ('CANCELLED', 'Cancelled'),
    ]

    aircraft = models.ForeignKey(Aircraft, related_name='flights', on_delete=models.PROTECT)
    flight_no = models.CharField(max_length=12, unique=True)
    airline = models.CharField(max_length=80)
    origin = models.CharField(max_length=80)
    destination = models.CharField(max_length=80)
    depart_at = models.DateTimeField()
    arrive_at = models.DateTimeField()
    base_price = models.DecimalField(max_digits=9, decimal_places=2)
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
    def seats_total(self):
        return self.seats.count() or self.aircraft.capacity

    @property
    def seats_booked(self):
        return self.bookings.filter(status='CONFIRMED').count()

    @property
    def seats_left(self):
        return max(self.seats_total - self.seats_booked, 0)

    @property
    def load_factor(self):
        return int((self.seats_booked / max(self.seats_total, 1)) * 100)

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
        latest_alert = self.delay_alerts.filter(active=True).order_by('-created_at').first()
        if latest_alert:
            return latest_alert.message
        if self.delay_minutes >= 180:
            return 'Hotel desk + meal voucher + free reschedule window active'
        if self.delay_minutes >= 90:
            return 'Meal voucher + priority rebooking support active'
        if self.delay_minutes > 0:
            return 'Delay alert sent with updated gate and time'
        return 'No accommodation needed'
