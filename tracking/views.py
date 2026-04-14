from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from flights.seed import ensure_seed_data

from .models import CheckEvent


def track_search(request):
    ensure_seed_data()
    if request.method == 'POST':
        pnr = request.POST.get('pnr', '').strip().upper()
        if pnr:
            return redirect('track_booking', pnr=pnr)
    return render(request, 'reservations/track_search.html')


def track_booking(request, pnr):
    ensure_seed_data()
    booking = get_object_or_404(Booking.objects.select_related('flight', 'seat', 'passenger', 'agent'), pnr=pnr.upper())
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'submit_docs':
            booking.document_status = 'SUBMITTED'
            booking.save()
            CheckEvent.objects.create(booking=booking, event_type='DOCUMENT', status='SUBMITTED', note='Passenger uploaded documents for C&D verification.')
            messages.success(request, 'Document check submitted for verification.')
        elif action == 'clear_docs':
            booking.document_status = 'CLEARED'
            booking.save()
            CheckEvent.objects.create(booking=booking, event_type='DOCUMENT', status='CLEARED', note='C&D document check cleared by operations desk.')
            messages.success(request, 'Document check cleared.')
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
