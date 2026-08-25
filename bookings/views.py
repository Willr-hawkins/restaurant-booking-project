from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from datetime import datetime

from .forms import BookingSearchForm, GuestDetailsForm
from .models import Booking
from .availability import get_available_slots, find_best_table_or_combination, find_next_available_date, predict_duration

def booking_widget(request):
    form = BookingSearchForm()
    return render(request, 'bookings/booking_widget.html', {'form': form})

def booking_slots(request):
    """ HTMX endpoint = returns the slot list partial for a given date/party size. """
    date_str = request.GET.get('date')
    party_size_str = request.GET.get('party_size')
    context = {}

    if date_str and party_size_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        party_size = int(party_size_str)
        candidate_slots = get_available_slots(date, party_size)
        real_slots = [s for s in candidate_slots if find_best_table_or_combination(date, s, party_size)]

        context['date'] = date
        context['party_size'] = party_size
        context['slots'] = real_slots

        if not real_slots:
            next_date, next_slot = find_next_available_date(date, party_size)
            context['next_date'] = next_date
            context['next_slot'] = next_slot

    return render(request, 'bookings/partials/slot_list.html', context)

def booking_details(request):
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    party_size_str = request.GET.get('party_size')

    if not (date_str and time_str and party_size_str):
        return redirect('booking_widget')
    
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    slot_time = datetime.strptime(time_str, '%H:%M').time()
    party_size = int(party_size_str)

    if request.method == 'POST':
        form = GuestDetailsForm(request.POST)
        if form.is_valid():
            request.session['pending_booking'] = {
                'date': date_str,
                'time': time_str,
                'party_size': party_size,
                **form.cleaned_data,
            }
            return redirect('booking_confirm')  # built in the next task!
    else:
        form = GuestDetailsForm()

    return render(request, 'bookings/booking_details.html', {
        'form': form,
        'date': date,
        'time': slot_time,
        'party_size': party_size,
    })

def booking_confirm(request):
    pending = request.session.get('pending_booking')
    if not pending:
        return redirect('booking_widget')
    
    date = datetime.strptime(pending['date'], '%Y-%m-%d').date()
    slot_time = datetime.strptime(pending['time'], '%H:%M').time()
    party_size = pending['party_size']

    assigned = find_best_table_or_combination(date, slot_time, party_size)
    if not assigned:
        # Someone else took the last available table between form load and submission
        messages.error(request, 'Sorry, that slot was just booked. Please choose another time.')
        del request.session['pending_booking']
        return redirect('booking_widget')
    
    duration = predict_duration(party_size, slot_time)
    content_type = ContentType.objects.get_for_model(assigned)

    booking = Booking.objects.create(
        guest_name=pending['guest_name'],
        guest_email=pending['guest_email'],
        guest_phone=pending['guest_phone'],
        date=date,
        time=slot_time,
        party_size=party_size,
        special_requests=pending.get('special_requests', ''),
        seating_preference=pending.get('seating_preference', ''),
        table_content_type=content_type,
        table_object_id=assigned.id,
        predicted_duration_minutes=duration,
        buffer_minutes=15,
        status='confirmed',
        deposit_required=party_size >= 6,
    )

    del request.session['pending_booking']

    return render(request, 'bookings/booking_confirm.html', {'booking': booking, 'assigned': assigned})
