from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Passenger
from agents.models import Agent
from bookings.models import Booking, Coupon
from seats.models import Seat

from .models import Aircraft, Flight
from .seed import ensure_seed_data


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
    return render(request, 'reservations/home.html', {'flights': flights, 'coupons': coupons})


def dashboard(request):
    ensure_seed_data()
    context = {
        'flight_count': Flight.objects.count(),
        'aircraft_count': Aircraft.objects.count(),
        'booking_count': Booking.objects.count(),
        'revenue': sum(booking.total_amount for booking in Booking.objects.filter(status='CONFIRMED')),
        'recent_bookings': Booking.objects.select_related('flight', 'seat', 'passenger', 'agent')[:8],
        'delayed_flights': Flight.objects.filter(status='DELAYED'),
        'agent_count': Agent.objects.filter(active=True).count(),
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
