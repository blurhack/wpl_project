from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from accounts.models import Passenger
from agents.models import Agent
from bookings.models import Booking, Coupon
from chatbot.models import FAQEntry
from delays.models import DelayAlert
from seats.models import Seat

from .models import Aircraft, City, Flight


CITY_DATA = [
    ('Hyderabad', 'HYD', 'Rajiv Gandhi International Airport'),
    ('Delhi', 'DEL', 'Indira Gandhi International Airport'),
    ('Bengaluru', 'BLR', 'Kempegowda International Airport'),
    ('Mumbai', 'BOM', 'Chhatrapati Shivaji Maharaj International Airport'),
    ('Chennai', 'MAA', 'Chennai International Airport'),
    ('Kolkata', 'CCU', 'Netaji Subhas Chandra Bose International Airport'),
    ('Goa', 'GOX', 'Manohar International Airport'),
    ('Kochi', 'COK', 'Cochin International Airport'),
    ('Pune', 'PNQ', 'Pune International Airport'),
    ('Jaipur', 'JAI', 'Jaipur International Airport'),
]

ROUTES = [
    ('SKY101', 'Indigo Nova', 'Hyderabad', 'Delhi', 6, 'A4', 'CHECKIN', 0),
    ('SKY204', 'Vistara Pulse', 'Bengaluru', 'Mumbai', 11, 'B2', 'ON_TIME', 0),
    ('SKY309', 'Air Prism', 'Chennai', 'Kolkata', 19, 'C7', 'DELAYED', 110),
    ('SKY412', 'CloudJet', 'Delhi', 'Goa', 28, 'D3', 'BOARDING', 0),
    ('SKY518', 'Indigo Nova', 'Mumbai', 'Hyderabad', 46, 'E1', 'DELAYED', 205),
    ('SKY620', 'Air Prism', 'Kochi', 'Bengaluru', 70, 'F5', 'ON_TIME', 0),
    ('SKY731', 'AeroMitra Express', 'Pune', 'Jaipur', 8, 'H2', 'CHECKIN', 0),
    ('SKY842', 'CloudJet', 'Jaipur', 'Chennai', 31, 'J4', 'ON_TIME', 0),
]

SAMPLE_PASSENGERS = [
    ('Aarav Mehta', 'aarav.mehta@example.com', '9876500011'),
    ('Diya Reddy', 'diya.reddy@example.com', '9876500022'),
    ('Kabir Rao', 'kabir.rao@example.com', '9876500033'),
    ('Meera Iyer', 'meera.iyer@example.com', '9876500044'),
    ('Nikhil Verma', 'nikhil.verma@example.com', '9876500055'),
    ('Sana Khan', 'sana.khan@example.com', '9876500066'),
]


def seed_cities():
    for name, code, airport in CITY_DATA:
        City.objects.get_or_create(name=name, defaults={'airport_code': code, 'airport_name': airport})


def seed_coupons():
    coupons = [
        ('LAB10', 'Student demo coupon, 10 percent off', 'PERCENT', Decimal('10')),
        ('FIRST500', 'Flat 500 off for first booking', 'FLAT', Decimal('500')),
        ('AGENT7', 'Agent desk coupon, 7 percent off', 'PERCENT', Decimal('7')),
        ('SKYFEST', 'Festival fare saver, 12 percent off', 'PERCENT', Decimal('12')),
        ('DELAYCARE', 'Care coupon for delayed route passengers', 'FLAT', Decimal('750')),
    ]
    for code, description, discount_type, value in coupons:
        Coupon.objects.get_or_create(code=code, defaults={'description': description, 'discount_type': discount_type, 'value': value})


def seed_agents():
    agents = [
        ('AGT1001', 'Pranith Desk', 'pranith.agent@aeromitra.test', '9000000001', 'Counter A'),
        ('AGT1002', 'Mitra Travel Support', 'support.agent@aeromitra.test', '9000000002', 'Counter B'),
        ('AGT1003', 'SkyBridge Corporate', 'corporate.agent@aeromitra.test', '9000000003', 'Corporate Desk'),
    ]
    for employee_code, name, email, phone, desk in agents:
        Agent.objects.get_or_create(employee_code=employee_code, defaults={'name': name, 'email': email, 'phone': phone, 'desk': desk})


def seed_faqs():
    faqs = [
        ('coupon', 'Which coupon can I use?', 'Try LAB10, FIRST500, AGENT7, SKYFEST, or DELAYCARE. Coupons are stored in the database and can be added from Control Tower or Django Admin.'),
        ('delay', 'What happens if my flight is delayed?', 'After 90 minutes, meal support starts. After 180 minutes, hotel desk and free reschedule support are shown in tracking.'),
        ('seat', 'How does seat selection work?', 'Choose green seats for economy, amber for premium, and violet for business. The final price updates before booking.'),
        ('check', 'How do C&D checks work?', 'Open Live Tracking with your PNR, submit document check, then complete check-in when the flight allows it.'),
        ('agent', 'What is agent booking?', 'Agent booking mode lets a travel desk book on behalf of a passenger and stores the agent record on the ticket.'),
        ('admin', 'Can I add flight and city data?', 'Yes. Use Control Tower for fast demo entry or Django Admin for full database management.'),
    ]
    for keyword, question, answer in faqs:
        FAQEntry.objects.get_or_create(keyword=keyword, defaults={'question': question, 'answer': answer})


def default_aircraft():
    aircraft, _ = Aircraft.objects.get_or_create(
        tail_number='VT-AM101',
        defaults={'manufacturer': 'Airbus', 'model': 'A320 Neo Lab', 'capacity': 60, 'rows': 10, 'seats_per_row': 6},
    )
    Aircraft.objects.get_or_create(tail_number='VT-AM202', defaults={'manufacturer': 'Boeing', 'model': '737 MAX Lab', 'capacity': 60, 'rows': 10, 'seats_per_row': 6})
    return aircraft


def create_seats_for_flight(flight):
    if flight.seats.exists():
        return
    seats = []
    for row in range(1, flight.aircraft.rows + 1):
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


def create_delay_alert(flight):
    if flight.delay_alerts.exists():
        return
    if flight.delay_minutes >= 180:
        DelayAlert.objects.create(flight=flight, delay_minutes=flight.delay_minutes, reason='Operational rotation delay', accommodation_type='HOTEL', message='Hotel desk + meal voucher + free reschedule window active')
    elif flight.delay_minutes >= 90:
        DelayAlert.objects.create(flight=flight, delay_minutes=flight.delay_minutes, reason='Late aircraft arrival', accommodation_type='MEAL', message='Meal voucher + priority rebooking support active')


def seed_flights():
    aircraft = default_aircraft()
    now = timezone.now()
    for index, item in enumerate(ROUTES):
        flight_no, airline, origin, destination, hours, gate, status, delay = item
        base_price = Decimal('3800') + Decimal(index * 620)
        flight, _ = Flight.objects.get_or_create(
            flight_no=flight_no,
            defaults={
                'aircraft': aircraft,
                'airline': airline,
                'origin': origin,
                'destination': destination,
                'depart_at': now + timedelta(hours=hours),
                'arrive_at': now + timedelta(hours=hours + 2 + index % 3),
                'base_price': base_price,
                'gate': gate,
                'status': status,
                'delay_minutes': delay,
                'checkin_open': status in ['CHECKIN', 'BOARDING', 'DELAYED'],
                'document_check_required': True,
            },
        )
        create_seats_for_flight(flight)
        create_delay_alert(flight)


def seed_sample_bookings():
    flights = list(Flight.objects.all()[:6])
    coupons = list(Coupon.objects.filter(active=True))
    agents = list(Agent.objects.filter(active=True))
    if not flights:
        return
    for index, data in enumerate(SAMPLE_PASSENGERS):
        name, email, phone = data
        if Booking.objects.filter(email=email).exists():
            continue
        flight = flights[index % len(flights)]
        booked_ids = Booking.objects.filter(flight=flight, status='CONFIRMED').values_list('seat_id', flat=True)
        seat = flight.seats.exclude(id__in=booked_ids).filter(is_blocked=False).first()
        if not seat:
            continue
        passenger, _ = Passenger.objects.get_or_create(email=email, defaults={'full_name': name, 'phone': phone})
        mode = 'AGENT' if index % 3 == 0 else 'USER'
        agent = agents[index % len(agents)] if mode == 'AGENT' and agents else None
        Booking.objects.create(
            passenger=passenger,
            passenger_name=name,
            email=email,
            phone=phone,
            flight=flight,
            seat=seat,
            coupon=coupons[index % len(coupons)] if coupons else None,
            booking_mode=mode,
            agent=agent,
            agent_name=agent.name if agent else '',
            document_status='CLEARED' if index % 2 == 0 else 'SUBMITTED',
            checked_in=index % 2 == 0,
        )


def ensure_seed_data():
    seed_cities()
    seed_coupons()
    seed_agents()
    seed_faqs()
    seed_flights()
    seed_sample_bookings()
