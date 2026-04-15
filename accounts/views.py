from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from bookings.models import Booking
from flights.seed import ensure_seed_data


def login_view(request):
    ensure_seed_data()
    if request.user.is_authenticated:
        return redirect('dashboard' if request.user.is_staff else 'my_bookings')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Logged in as {user.username}.')
            return redirect('dashboard' if user.is_staff else 'my_bookings')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'reservations/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


@login_required
def my_bookings(request):
    ensure_seed_data()
    if request.user.is_staff:
        bookings = Booking.objects.select_related('flight', 'seat', 'passenger', 'agent').all()[:30]
    else:
        bookings = Booking.objects.select_related('flight', 'seat', 'passenger', 'agent').filter(passenger__user=request.user)
    return render(request, 'reservations/my_bookings.html', {'bookings': bookings})
