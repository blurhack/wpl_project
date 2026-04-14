from django.db import models


class CheckEvent(models.Model):
    EVENT_CHOICES = [
        ('DOCUMENT', 'Document Check'),
        ('CHECKIN', 'Check-in'),
        ('GATE', 'Gate Update'),
        ('DELAY', 'Delay Update'),
    ]

    booking = models.ForeignKey('bookings.Booking', related_name='check_events', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    status = models.CharField(max_length=40)
    note = models.CharField(max_length=180)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking.pnr} · {self.event_type}'
