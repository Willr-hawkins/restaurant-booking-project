from django.shortcuts import render, redirect
from datetime import datetime

from .forms import BookingSearchForm, GuestDetailsForm
from .availability import get_available_slots, find_best_table_or_combination, find_next_available_date

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