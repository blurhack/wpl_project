from django.db import models


class DelayAlert(models.Model):
    ACCOMMODATION_CHOICES = [
        ('NONE', 'No Accommodation'),
        ('MEAL', 'Meal Voucher'),
        ('HOTEL', 'Hotel + Meal'),
        ('REBOOK', 'Priority Rebooking'),
    ]

    flight = models.ForeignKey('flights.Flight', related_name='delay_alerts', on_delete=models.CASCADE)
    delay_minutes = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=140)
    accommodation_type = models.CharField(max_length=20, choices=ACCOMMODATION_CHOICES, default='NONE')
    message = models.CharField(max_length=220)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.flight.flight_no} · {self.delay_minutes} min'
