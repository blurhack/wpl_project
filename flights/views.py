from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Passenger
from agents.models import Agent
from bookings.models import Booking, Coupon
from delays.models import DelayAlert
from seats.models import Seat

from .models import Aircraft, City, Flight
from .seed import create_seats_for_flight, ensure_seed_data


def home(request):
    ensure_seed_data()
    flights = Flight.objects.select_related('aircraft').all()
    origin = request.GET.get('origin', '').strip()
    destination = request.GET.get('destination', '').strip()
    query = request.GET.get('q', '').strip()
    if origin:
        flights = flights.filter(origin__icontains=origin)
    if destination:
        flights = flights.filter(destination__icontains=destination)
    if query:
        flights = flights.filter(Q(flight_no__icontains=query) | Q(airline__icontains=query))
    coupons = Coupon.objects.filter(active=True)
    context = {
        'flights': flights,
        'coupons': coupons,
        'cities': City.objects.filter(active=True),
        'live_booking_count': Booking.objects.count(),
        'delayed_count': Flight.objects.filter(status='DELAYED').count(),
    }
    return render(request, 'reservations/home.html', context)


def dashboard(request):
    ensure_seed_data()
    context = {
        'flight_count': Flight.objects.count(),
        'aircraft_count': Aircraft.objects.count(),
        'city_count': City.objects.count(),
        'booking_count': Booking.objects.count(),
        'revenue': sum(booking.total_amount for booking in Booking.objects.filter(status='CONFIRMED')),
        'recent_bookings': Booking.objects.select_related('flight', 'seat', 'passenger', 'agent')[:8],
        'delayed_flights': Flight.objects.filter(status='DELAYED'),
        'agent_count': Agent.objects.filter(active=True).count(),
        'coupons': Coupon.objects.filter(active=True),
    }
    return render(request, 'reservations/dashboard.html', context)


def flight_detail(request, flight_id):
    ensure_seed_data()
    flight = get_object_or_404(Flight, id=flight_id)
    seats = flight.seats.all()
    booked_seat_ids = set(Booking.objects.filter(flight=flight, status='CONFIRMED').values_list('seat_id', flat=True))
    coupons = Coupon.objects.filter(active=True)
    mode = request.GET.get('mode', 'USER')

    if request.method == 'POST':
        seat_id = request.POST.get('seat_id')
        passenger_name = request.POST.get('passenger_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        booking_mode = request.POST.get('booking_mode', 'USER')
        agent_name = request.POST.get('agent_name', '').strip()
        coupon_code = request.POST.get('coupon_code', '').strip().upper()

        if not seat_id or not passenger_name or not email or not phone:
            messages.error(request, 'Please select a seat and fill passenger details.')
            return redirect('flight_detail', flight_id=flight.id)

        seat = get_object_or_404(Seat, id=seat_id, flight=flight)
        if seat.is_blocked or seat.id in booked_seat_ids:
            messages.error(request, 'That seat was just taken. Please choose another seat.')
            return redirect('flight_detail', flight_id=flight.id)

        coupon = None
        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code, active=True).first()
            if not coupon:
                messages.error(request, 'Coupon code is not valid for this booking.')
                return redirect('flight_detail', flight_id=flight.id)

        passenger, _ = Passenger.objects.get_or_create(
            email=email,
            defaults={'full_name': passenger_name, 'phone': phone},
        )
        passenger.full_name = passenger_name
        passenger.phone = phone
        passenger.save()

        agent = None
        if booking_mode == 'AGENT':
            agent = Agent.objects.filter(name__icontains=agent_name).first() or Agent.objects.filter(active=True).first()

        booking = Booking.objects.create(
            passenger=passenger,
            passenger_name=passenger_name,
            email=email,
            phone=phone,
            flight=flight,
            seat=seat,
            coupon=coupon,
            booking_mode=booking_mode if booking_mode in ['USER', 'AGENT'] else 'USER',
            agent=agent,
            agent_name=agent_name if booking_mode == 'AGENT' else '',
            document_status='PENDING' if flight.document_check_required else 'CLEARED',
        )
        messages.success(request, f'Booking confirmed. PNR: {booking.pnr}')
        return redirect('track_booking', pnr=booking.pnr)

    return render(request, 'reservations/flight_detail.html', {
        'flight': flight,
        'seats': seats,
        'booked_seat_ids': booked_seat_ids,
        'coupons': coupons,
        'mode': mode,
    })


def control_tower(request):
    ensure_seed_data()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_city':
            City.objects.get_or_create(
                name=request.POST.get('name', '').strip(),
                defaults={
                    'airport_code': request.POST.get('airport_code', '').strip().upper(),
                    'airport_name': request.POST.get('airport_name', '').strip(),
                    'country': request.POST.get('country', 'India').strip() or 'India',
                },
            )
            messages.success(request, 'City and airport added to the database.')
        elif action == 'add_coupon':
            code = request.POST.get('code', '').strip().upper()
            Coupon.objects.update_or_create(
                code=code,
                defaults={
                    'description': request.POST.get('description', '').strip(),
                    'discount_type': request.POST.get('discount_type', 'PERCENT'),
                    'value': Decimal(request.POST.get('value', '0') or '0'),
                    'active': True,
                },
            )
            messages.success(request, 'Coupon saved and available in booking/chatbot.')
        elif action == 'add_flight':
            origin = get_object_or_404(City, id=request.POST.get('origin_city'))
            destination = get_object_or_404(City, id=request.POST.get('destination_city'))
            aircraft = Aircraft.objects.first()
            depart_at = timezone.now() + timedelta(hours=int(request.POST.get('hours_from_now', '12') or '12'))
            arrive_at = depart_at + timedelta(hours=int(request.POST.get('duration_hours', '2') or '2'))
            flight = Flight.objects.create(
                aircraft=aircraft,
                flight_no=request.POST.get('flight_no', '').strip().upper(),
                airline=request.POST.get('airline', 'AeroMitra Express').strip(),
                origin=origin.name,
                destination=destination.name,
                depart_at=depart_at,
                arrive_at=arrive_at,
                base_price=Decimal(request.POST.get('base_price', '4500') or '4500'),
                gate=request.POST.get('gate', 'K1').strip().upper(),
                status=request.POST.get('status', 'ON_TIME'),
                delay_minutes=int(request.POST.get('delay_minutes', '0') or '0'),
                checkin_open=request.POST.get('status') in ['CHECKIN', 'BOARDING', 'DELAYED'],
                document_check_required=True,
            )
            create_seats_for_flight(flight)
            if flight.delay_minutes:
                DelayAlert.objects.create(flight=flight, delay_minutes=flight.delay_minutes, reason='Control Tower update', accommodation_type='MEAL' if flight.delay_minutes < 180 else 'HOTEL', message=flight.delay_support)
            messages.success(request, f'Flight {flight.flight_no} created with full seat map.')
        elif action == 'sample_booking':
            flight = get_object_or_404(Flight, id=request.POST.get('flight_id'))
            booked_ids = Booking.objects.filter(flight=flight, status='CONFIRMED').values_list('seat_id', flat=True)
            seat = flight.seats.exclude(id__in=booked_ids).filter(is_blocked=False).first()
            if not seat:
                messages.error(request, 'No free seats left on that flight.')
            else:
                passenger, _ = Passenger.objects.get_or_create(
                    email=request.POST.get('email', 'sample.passenger@example.com').strip(),
                    defaults={'full_name': request.POST.get('passenger_name', 'Sample Passenger').strip(), 'phone': request.POST.get('phone', '9999999999').strip()},
                )
                passenger.full_name = request.POST.get('passenger_name', passenger.full_name).strip()
                passenger.phone = request.POST.get('phone', passenger.phone).strip()
                passenger.save()
                coupon = Coupon.objects.filter(code=request.POST.get('coupon_code', '').strip().upper(), active=True).first()
                agent = Agent.objects.filter(active=True).first()
                booking = Booking.objects.create(
                    passenger=passenger,
                    passenger_name=passenger.full_name,
                    email=passenger.email,
                    phone=passenger.phone,
                    flight=flight,
                    seat=seat,
                    coupon=coupon,
                    booking_mode='AGENT' if agent else 'USER',
                    agent=agent,
                    agent_name=agent.name if agent else '',
                    document_status='SUBMITTED',
                )
                messages.success(request, f'Sample booking created. PNR: {booking.pnr}')
        return redirect('control_tower')

    context = {
        'cities': City.objects.all(),
        'flights': Flight.objects.select_related('aircraft').all(),
        'coupons': Coupon.objects.all(),
        'bookings': Booking.objects.select_related('flight', 'seat', 'passenger', 'agent')[:12],
        'aircraft': Aircraft.objects.all(),
        'statuses': Flight.STATUS_CHOICES,
    }
    return render(request, 'reservations/control_tower.html', context)
