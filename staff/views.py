from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from staff.decorators import staff_required
from bookings.models import Booking

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'staff_profile'):
            login(request, user)
            return redirect('staff_dashboard') # placeholder - built in Sprint 5
        return render(request, 'staff/login.html', {'error': 'Invalid credentials'})
    return render(request, 'staff/login.html')

@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')

@staff_required
def staff_dashboard(request):
    context = {}
    profile = getattr(request.user, 'staff_profile', None)

    if profile and profile.is_manager:
        today = timezone.localtime().date()
        week_end = today + timedelta(days=7)

        todays_bookings = list(Booking.objects.filter(date=today, status='confirmed').order_by('time'))
        todays_covers = sum(b.party_size for b in todays_bookings)

        no_show_counts = dict(
            Booking.objects.filter(status='no_show')
            .values('guest_email')
            .annotate(count=Count('id'))
            .values_list('guest_email', 'count')
        )
        for b in todays_bookings:
            b.guest_no_show_count = no_show_counts.get(b.guest_email, 0)

        upcoming_week = Booking.objects.filter(
            date__gt=today, date__lte=week_end, status='confirmed'
        ).order_by('date', 'time')

        context.update({
            'is_manager': True,
            'todays_bookings': todays_bookings,
            'todays_covers': todays_covers,
            'todays_booking_count': len(todays_bookings),
            'upcoming_week': upcoming_week,
            'upcoming_week_count': upcoming_week.count(),
        })

    return render(request, 'staff/dashboard.html', context)