from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from .models import Coupon, Flight, Seat


ROUTES = [
    ('SKY101', 'Indigo Nova', 'Hyderabad', 'Delhi', 6, 'A4', 'CHECKIN', 0),
    ('SKY204', 'Vistara Pulse', 'Bengaluru', 'Mumbai', 11, 'B2', 'ON_TIME', 0),
    ('SKY309', 'Air Prism', 'Chennai', 'Kolkata', 19, 'C7', 'DELAYED', 110),
    ('SKY412', 'CloudJet', 'Delhi', 'Goa', 28, 'D3', 'BOARDING', 0),
    ('SKY518', 'Indigo Nova', 'Mumbai', 'Hyderabad', 46, 'E1', 'DELAYED', 205),
    ('SKY620', 'Air Prism', 'Kochi', 'Bengaluru', 70, 'F5', 'ON_TIME', 0),
]


def ensure_seed_data():
    if not Coupon.objects.exists():
        Coupon.objects.bulk_create([
            Coupon(code='LAB10', description='Student demo coupon, 10 percent off', discount_type='PERCENT', value=Decimal('10')),
            Coupon(code='FIRST500', description='Flat 500 off for first booking', discount_type='FLAT', value=Decimal('500')),
            Coupon(code='AGENT7', description='Agent desk coupon, 7 percent off', discount_type='PERCENT', value=Decimal('7')),
        ])

    if Flight.objects.exists():
        return

    now = timezone.now()
    for index, item in enumerate(ROUTES):
        flight_no, airline, origin, destination, hours, gate, status, delay = item
        base_price = Decimal('3800') + Decimal(index * 650)
        flight = Flight.objects.create(
            flight_no=flight_no,
            airline=airline,
            origin=origin,
            destination=destination,
            depart_at=now + timedelta(hours=hours),
            arrive_at=now + timedelta(hours=hours + 2 + index % 3),
            base_price=base_price,
            seats_total=60,
            gate=gate,
            status=status,
            delay_minutes=delay,
            checkin_open=status in ['CHECKIN', 'BOARDING', 'DELAYED'],
            document_check_required=True,
        )
        seats = []
        for row in range(1, 11):
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                code = f'{row}{col}'
                if row <= 2:
                    cabin = 'Business'
                    modifier = Decimal('2600')
                elif row <= 4:
                    cabin = 'Premium'
                    modifier = Decimal('1100')
                else:
                    cabin = 'Economy'
                    modifier = Decimal('0')
                seats.append(Seat(flight=flight, code=code, cabin=cabin, price_modifier=modifier, is_blocked=False))
        Seat.objects.bulk_create(seats)
