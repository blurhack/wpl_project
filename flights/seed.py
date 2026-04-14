from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from agents.models import Agent
from bookings.models import Coupon
from chatbot.models import FAQEntry
from delays.models import DelayAlert
from seats.models import Seat

from .models import Aircraft, Flight


ROUTES = [
    ('SKY101', 'Indigo Nova', 'Hyderabad', 'Delhi', 6, 'A4', 'CHECKIN', 0),
    ('SKY204', 'Vistara Pulse', 'Bengaluru', 'Mumbai', 11, 'B2', 'ON_TIME', 0),
    ('SKY309', 'Air Prism', 'Chennai', 'Kolkata', 19, 'C7', 'DELAYED', 110),
    ('SKY412', 'CloudJet', 'Delhi', 'Goa', 28, 'D3', 'BOARDING', 0),
    ('SKY518', 'Indigo Nova', 'Mumbai', 'Hyderabad', 46, 'E1', 'DELAYED', 205),
    ('SKY620', 'Air Prism', 'Kochi', 'Bengaluru', 70, 'F5', 'ON_TIME', 0),
]


def seed_coupons():
    coupons = [
        ('LAB10', 'Student demo coupon, 10 percent off', 'PERCENT', Decimal('10')),
        ('FIRST500', 'Flat 500 off for first booking', 'FLAT', Decimal('500')),
        ('AGENT7', 'Agent desk coupon, 7 percent off', 'PERCENT', Decimal('7')),
    ]
    for code, description, discount_type, value in coupons:
        Coupon.objects.get_or_create(code=code, defaults={'description': description, 'discount_type': discount_type, 'value': value})


def seed_agents():
    agents = [
        ('AGT1001', 'Pranith Desk', 'pranith.agent@aeromitra.test', '9000000001', 'Counter A'),
        ('AGT1002', 'Mitra Travel Support', 'support.agent@aeromitra.test', '9000000002', 'Counter B'),
    ]
    for employee_code, name, email, phone, desk in agents:
        Agent.objects.get_or_create(employee_code=employee_code, defaults={'name': name, 'email': email, 'phone': phone, 'desk': desk})


def seed_faqs():
    faqs = [
        ('coupon', 'Which coupon can I use?', 'Try LAB10 for 10 percent off, FIRST500 for flat 500 off, or AGENT7 for agent desk bookings.'),
        ('delay', 'What happens if my flight is delayed?', 'After 90 minutes, meal support starts. After 180 minutes, hotel desk and free reschedule support are shown in tracking.'),
        ('seat', 'How does seat selection work?', 'Choose green seats for economy, amber for premium, and purple for business. The final price updates before booking.'),
        ('check', 'How do C&D checks work?', 'Open Live Tracking with your PNR, submit document check, then complete check-in when the flight allows it.'),
        ('agent', 'What is agent booking?', 'Agent booking mode lets a travel desk book on behalf of a passenger and stores the agent record on the ticket.'),
    ]
    for keyword, question, answer in faqs:
        FAQEntry.objects.get_or_create(keyword=keyword, defaults={'question': question, 'answer': answer})


def ensure_seed_data():
    seed_coupons()
    seed_agents()
    seed_faqs()

    if Flight.objects.exists():
        return

    aircraft = Aircraft.objects.create(tail_number='VT-AM101', manufacturer='Airbus', model='A320 Neo Lab', capacity=60, rows=10, seats_per_row=6)
    now = timezone.now()
    for index, item in enumerate(ROUTES):
        flight_no, airline, origin, destination, hours, gate, status, delay = item
        base_price = Decimal('3800') + Decimal(index * 650)
        flight = Flight.objects.create(
            aircraft=aircraft,
            flight_no=flight_no,
            airline=airline,
            origin=origin,
            destination=destination,
            depart_at=now + timedelta(hours=hours),
            arrive_at=now + timedelta(hours=hours + 2 + index % 3),
            base_price=base_price,
            gate=gate,
            status=status,
            delay_minutes=delay,
            checkin_open=status in ['CHECKIN', 'BOARDING', 'DELAYED'],
            document_check_required=True,
        )
        if delay >= 180:
            DelayAlert.objects.create(flight=flight, delay_minutes=delay, reason='Operational rotation delay', accommodation_type='HOTEL', message='Hotel desk + meal voucher + free reschedule window active')
        elif delay >= 90:
            DelayAlert.objects.create(flight=flight, delay_minutes=delay, reason='Late aircraft arrival', accommodation_type='MEAL', message='Meal voucher + priority rebooking support active')
        seats = []
        for row in range(1, aircraft.rows + 1):
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
                seats.append(Seat(flight=flight, code=code, cabin=cabin, price_modifier=modifier))
        Seat.objects.bulk_create(seats)
