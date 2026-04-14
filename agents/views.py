from django.shortcuts import render

from bookings.models import Booking
from flights.models import Flight
from flights.seed import ensure_seed_data

from .models import Agent


def agent_booking(request):
    ensure_seed_data()
    flights = Flight.objects.select_related('aircraft').all()
    recent = Booking.objects.select_related('flight', 'seat', 'agent').filter(booking_mode='AGENT')[:6]
    agents = Agent.objects.filter(active=True)
    return render(request, 'reservations/agent.html', {'flights': flights, 'recent': recent, 'agents': agents})
