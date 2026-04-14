from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Booking, Coupon, Flight, Seat
from .seed import ensure_seed_data


def priced_amount(flight, seat, coupon):
    amount = flight.dynamic_price + seat.price_modifier
    if coupon:
        amount = coupon.apply(amount)
    return amount.quantize(Decimal('1'))


def home(request):
    ensure_seed_data()
    flights = Flight.objects.all()
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


def flight_detail(request, flight_id):
    ensure_seed_data()
    flight = get_object_or_404(Flight, id=flight_id)
    seats = flight.seats.all()
    booked_seat_ids = set(Booking.objects.filter(flight=flight, status='CONFIRMED').values_list('seat_id', flat=True))
    coupons = Coupon.objects.filter(active=True)

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

        total = priced_amount(flight, seat, coupon)
        booking = Booking.objects.create(
            passenger_name=passenger_name,
            email=email,
            phone=phone,
            flight=flight,
            seat=seat,
            coupon=coupon,
            booking_mode=booking_mode if booking_mode in ['USER', 'AGENT'] else 'USER',
            agent_name=agent_name if booking_mode == 'AGENT' else '',
            total_amount=total,
            document_status='PENDING' if flight.document_check_required else 'CLEARED',
            accommodation_note=flight.delay_support,
        )
        messages.success(request, f'Booking confirmed. PNR: {booking.pnr}')
        return redirect('track_booking', pnr=booking.pnr)

    return render(request, 'reservations/flight_detail.html', {
        'flight': flight,
        'seats': seats,
        'booked_seat_ids': booked_seat_ids,
        'coupons': coupons,
        'mode': request.GET.get('mode', 'USER'),
    })


def agent_booking(request):
    ensure_seed_data()
    flights = Flight.objects.all()
    recent = Booking.objects.filter(booking_mode='AGENT')[:6]
    return render(request, 'reservations/agent.html', {'flights': flights, 'recent': recent})


def track_search(request):
    ensure_seed_data()
    if request.method == 'POST':
        pnr = request.POST.get('pnr', '').strip().upper()
        if pnr:
            return redirect('track_booking', pnr=pnr)
    return render(request, 'reservations/track_search.html')


def track_booking(request, pnr):
    ensure_seed_data()
    booking = get_object_or_404(Booking, pnr=pnr.upper())
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'submit_docs':
            booking.document_status = 'SUBMITTED'
            booking.save()
            messages.success(request, 'Document check submitted for verification.')
        elif action == 'clear_docs':
            booking.document_status = 'CLEARED'
            booking.save()
            messages.success(request, 'Document check cleared.')
        elif action == 'check_in':
            if booking.flight.checkin_open and booking.document_status in ['SUBMITTED', 'CLEARED']:
                booking.checked_in = True
                booking.save()
                messages.success(request, 'Check-in completed. Boarding pass status is active.')
            else:
                messages.error(request, 'Complete document check first or wait for check-in to open.')
        return redirect('track_booking', pnr=booking.pnr)
    return render(request, 'reservations/track.html', {'booking': booking})


def bot_reply(text):
    text = text.lower()
    if 'coupon' in text or 'discount' in text:
        return 'Try LAB10 for 10 percent off, FIRST500 for flat 500 off, or AGENT7 for agent desk bookings.'
    if 'delay' in text or 'late' in text:
        return 'If delay crosses 90 minutes, meal support starts. After 180 minutes, hotel desk and free reschedule support are shown in tracking.'
    if 'seat' in text:
        return 'Choose green seats for economy, amber for premium, and purple for business. The price updates before booking.'
    if 'check' in text or 'document' in text:
        return 'Open Live Tracking with your PNR, submit document check, then complete check-in when the flight allows it.'
    if 'agent' in text:
        return 'Agent booking mode lets a travel desk book on behalf of a passenger and stores the agent name on the ticket.'
    return 'I can help with coupons, seat selection, flight delay support, agent booking, and check-in/document status.'


def chatbot(request):
    ensure_seed_data()
    chat = request.session.get('chat', [])
    if not chat:
        chat = [{'role': 'bot', 'text': 'Hi, I am AeroBot. Ask me about coupons, delays, seats, or check-in.'}]
    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            chat.append({'role': 'user', 'text': text})
            chat.append({'role': 'bot', 'text': bot_reply(text)})
            request.session['chat'] = chat[-12:]
        return redirect('chatbot')
    return render(request, 'reservations/chatbot.html', {'chat': chat})
