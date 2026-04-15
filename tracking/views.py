from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from bookings.models import Booking
from flights.seed import ensure_seed_data

from .models import CheckEvent


def aviationstack_url(flight_number):
    params = {'access_key': settings.AVIATIONSTACK_ACCESS_KEY, 'flight_iata': flight_number}
    return f'https://api.aviationstack.com/v1/flights?{urlencode(params)}'


def track_search(request):
    ensure_seed_data()
    if request.method == 'POST':
        value = request.POST.get('pnr', '').strip().upper()
        if value:
            booking = Booking.objects.filter(pnr=value).first()
            if booking:
                return redirect('track_booking', pnr=booking.pnr)
            flight_booking = Booking.objects.filter(flight__flight_no=value).first()
            if flight_booking:
                return redirect('track_booking', pnr=flight_booking.pnr)
            if settings.AVIATIONSTACK_ACCESS_KEY:
                return HttpResponseRedirect(aviationstack_url(value))
            messages.error(request, 'No local PNR found. To redirect flight-number tracking to Aviationstack, set AVIATIONSTACK_ACCESS_KEY in environment variables.')
    return render(request, 'reservations/track_search.html')


def track_booking(request, pnr):
    ensure_seed_data()
    booking = Booking.objects.select_related('flight', 'seat', 'passenger', 'agent').filter(pnr=pnr.upper()).first()
    if not booking:
        messages.error(request, 'PNR was not found. Enter a valid PNR or a flight number for Aviationstack lookup.')
        return redirect('track_search')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'submit_docs':
            booking.document_status = 'SUBMITTED'
            booking.save()
            CheckEvent.objects.create(booking=booking, event_type='DOCUMENT', status='SUBMITTED', note='Passenger uploaded documents for C&D verification.')
            messages.success(request, 'Document check submitted for verification.')
        elif action == 'clear_docs':
            if request.user.is_staff:
                booking.document_status = 'CLEARED'
                booking.save()
                CheckEvent.objects.create(booking=booking, event_type='DOCUMENT', status='CLEARED', note='C&D document check cleared by operations desk.')
                messages.success(request, 'Document check cleared.')
            else:
                messages.error(request, 'Only admin/operations can clear document checks.')
        elif action == 'check_in':
            if booking.flight.checkin_open and booking.document_status in ['SUBMITTED', 'CLEARED']:
                booking.checked_in = True
                booking.save()
                CheckEvent.objects.create(booking=booking, event_type='CHECKIN', status='COMPLETED', note='Passenger check-in completed and boarding status activated.')
                messages.success(request, 'Check-in completed. Boarding pass status is active.')
            else:
                messages.error(request, 'Complete document check first or wait for check-in to open.')
        return redirect('track_booking', pnr=booking.pnr)
    events = booking.check_events.all()[:8]
    return render(request, 'reservations/track.html', {'booking': booking, 'events': events})
