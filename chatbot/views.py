from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.models import Passenger
from bookings.models import Booking, Coupon
from flights.models import Flight
from flights.seed import ensure_seed_data
from seats.models import Seat

from .models import ChatMessage, FAQEntry


def bot_reply(text):
    lowered = text.lower()
    if 'book' in lowered or 'ticket' in lowered:
        return 'I can book a ticket here. Use the quick booking form beside this chat, choose a flight, enter passenger details and I will create the PNR.'
    for faq in FAQEntry.objects.filter(active=True):
        if faq.keyword.lower() in lowered or any(word in lowered for word in faq.question.lower().split()[:3]):
            return faq.answer
    return 'I can help with ticket booking, coupons, seat selection, flight delay support, agent booking, and check-in/document status.'


def chatbot(request):
    ensure_seed_data()
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    if not ChatMessage.objects.filter(session_key=session_key).exists():
        ChatMessage.objects.create(session_key=session_key, role='bot', text='Hi, I am AeroBot. I can answer questions and book tickets. Try asking "book ticket" or use the quick booking form.')
    if request.method == 'POST':
        action = request.POST.get('action', 'chat')
        if action == 'book_ticket':
            flight = Flight.objects.filter(id=request.POST.get('flight_id')).first()
            passenger_name = request.POST.get('passenger_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            coupon_code = request.POST.get('coupon_code', '').strip().upper()
            if not flight or not passenger_name or not email or not phone:
                messages.error(request, 'AeroBot needs flight, passenger name, email and phone to book.')
            else:
                booked_ids = Booking.objects.filter(flight=flight, status='CONFIRMED').values_list('seat_id', flat=True)
                seat = Seat.objects.filter(flight=flight, is_blocked=False).exclude(id__in=booked_ids).first()
                if not seat:
                    messages.error(request, 'AeroBot could not book because this flight has no free seats.')
                else:
                    passenger, _ = Passenger.objects.get_or_create(email=email, defaults={'full_name': passenger_name, 'phone': phone})
                    passenger.full_name = passenger_name
                    passenger.phone = phone
                    if request.user.is_authenticated and not request.user.is_staff:
                        passenger.user = request.user
                    passenger.save()
                    coupon = Coupon.objects.filter(code=coupon_code, active=True).first() if coupon_code else None
                    booking = Booking.objects.create(
                        passenger=passenger,
                        passenger_name=passenger.full_name,
                        email=passenger.email,
                        phone=passenger.phone,
                        flight=flight,
                        seat=seat,
                        coupon=coupon,
                        booking_mode='USER',
                        document_status='PENDING' if flight.document_check_required else 'CLEARED',
                    )
                    ChatMessage.objects.create(session_key=session_key, role='user', text=f'Book ticket on {flight.flight_no}')
                    ChatMessage.objects.create(session_key=session_key, role='bot', text=f'Ticket booked successfully. Your PNR is {booking.pnr}. Open My Bookings or Live Tracking to continue.')
                    messages.success(request, f'AeroBot booked your ticket. PNR: {booking.pnr}')
                    return redirect('track_booking', pnr=booking.pnr)
        else:
            text = request.POST.get('message', '').strip()
            if text:
                ChatMessage.objects.create(session_key=session_key, role='user', text=text)
                ChatMessage.objects.create(session_key=session_key, role='bot', text=bot_reply(text))
        return redirect('chatbot')
    chat = ChatMessage.objects.filter(session_key=session_key).order_by('created_at')
    context = {
        'chat': chat,
        'flights': Flight.objects.select_related('aircraft').all(),
        'coupons': Coupon.objects.filter(active=True),
    }
    return render(request, 'reservations/chatbot.html', context)
