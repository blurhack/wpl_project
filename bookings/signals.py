from decimal import Decimal

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from tracking.models import CheckEvent

from .models import Booking, Payment


@receiver(pre_save, sender=Booking)
def apply_dynamic_booking_price(sender, instance, **kwargs):
    if not instance.passenger_name and instance.passenger:
        instance.passenger_name = instance.passenger.full_name
    if not instance.email and instance.passenger:
        instance.email = instance.passenger.email
    if not instance.phone and instance.passenger:
        instance.phone = instance.passenger.phone
    if instance.agent and not instance.agent_name:
        instance.agent_name = instance.agent.name
    if instance.seat_id and instance.flight_id:
        amount = Decimal(instance.flight.dynamic_price) + Decimal(instance.seat.price_modifier)
        if instance.coupon:
            amount = instance.coupon.apply(amount)
        instance.total_amount = amount.quantize(Decimal('1'))
    if instance.flight_id and not instance.accommodation_note:
        instance.accommodation_note = instance.flight.delay_support


@receiver(post_save, sender=Booking)
def create_payment_and_initial_checks(sender, instance, created, **kwargs):
    if created:
        Payment.objects.get_or_create(
            booking=instance,
            defaults={
                'amount': instance.total_amount,
                'status': 'PAID',
                'transaction_id': f'PAY{instance.pnr}',
            },
        )
        CheckEvent.objects.create(
            booking=instance,
            event_type='DOCUMENT',
            status=instance.document_status,
            note='Passenger document check opened for this PNR.',
        )
        CheckEvent.objects.create(
            booking=instance,
            event_type='GATE',
            status=instance.flight.status,
            note=f'Gate {instance.flight.gate} assigned for {instance.flight.flight_no}.',
        )
