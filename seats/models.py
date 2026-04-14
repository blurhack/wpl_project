from django.db import models


class Seat(models.Model):
    CABIN_CHOICES = [
        ('Economy', 'Economy'),
        ('Premium', 'Premium'),
        ('Business', 'Business'),
    ]

    flight = models.ForeignKey('flights.Flight', related_name='seats', on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    cabin = models.CharField(max_length=20, choices=CABIN_CHOICES, default='Economy')
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['flight', 'code']
        ordering = ['code']

    def __str__(self):
        return f'{self.flight.flight_no} {self.code}'
