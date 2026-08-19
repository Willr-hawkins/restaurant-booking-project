from django.shortcuts import render
from datetime import datetime

from .forms import BookingSearchForm
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

