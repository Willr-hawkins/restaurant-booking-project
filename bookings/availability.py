from datetime import datetime, timedelta, time
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import Service, SpecialHours, Booking
from tables.models import Table

# Duration rules: (max_party_size, lunch_minutes, dinner_minutes)
# Lunch tends to turn faster than dinner for the same party size
DURATION_RULES = [
    (2, 75, 90),
    (4, 90, 105),
    (6, 105, 120),
    (999, 120, 150),
]

LUNCH_CUTOFF = time(16, 0) # bookings before this are treated as "lunch" pacing

def get_available_slots(date, party_size=None):
    """
    Returns a sorted list of time objects representing valid booking slots
    for the given date, based on Service definitions and any SpecialHours override.
    """
    special = SpecialHours.objects.filter(date=date).first()

    if special:
        if special.is_closed:
            return []
        if special.custom_start_time and special.custom_end_time:
            # One-off override replaces the normal Service entirely for this date
            slots = _generate_slots(
                special.custom_start_time,
                special.custom_end_time,
                last_booking_time=special.custom_end_time,
                slot_interval_minutes=30,
            )
            return _filter_past_slots(date, slots)
    
    day_of_week = date.weekday()
    services = Service.objects.filter(day_of_week=day_of_week, is_active=True)

    slots = []
    for service in services:
        slots.extend(_generate_slots(
            service.start_time,
            service.end_time,
            service.last_booking_time,
            service.slot_interval_minutes,
        ))

    slots = sorted(set(slots))
    return _filter_past_slots(date, slots)

def _generate_slots(start_time, end_time, last_booking_time, slot_interval_minutes):
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    cutoff = datetime.combine(datetime.today(), last_booking_time)
    while current <= cutoff:
        slots.append(current.time())
        current += timedelta(minutes=slot_interval_minutes)
    return slots

def _filter_past_slots(date, slots):
    """ If booking for today, exclude slots that have already passed. """
    now = timezone.localtime()
    if date != now.date():
        return slots
    return [s for s in slots if s > now.time()]

def is_table_free(table_or_combo, date, start_time, duration_minutes):
    """
    Check whether a Table or TableCombination is free at the given date/start_time
    for the given duration, accounting for existing bookings' duration + buffer.
    """
    content_type = ContentType.objects.get_for_model(table_or_combo)
    existing_bookings = Booking.objects.filter(
        table_content_type=content_type,
        table_object_id=table_or_combo.id,
        date=date,
        status='confirmed',
    )

    new_start = datetime.combine(date, start_time)
    new_end = new_start + timedelta(minutes=duration_minutes)

    for booking in existing_bookings:
        existing_start = datetime.combine(date, booking.time)
        occupied_minutes = booking.predicted_duration_minutes + booking.buffer_minutes
        existing_end = existing_start + timedelta(minutes=occupied_minutes)

        if new_start < existing_end and new_end > existing_start:
            return False
        
    return True

def predict_duration(party_size, start_time):
    """ Estimate how long a table will be occupied, based on party size and time of day. """
    is_lunch = start_time < LUNCH_CUTOFF
    for max_size, lunch_minutes, dinner_minutes in DURATION_RULES:
        if party_size <= max_size:
            return lunch_minutes if is_lunch else dinner_minutes
    return DURATION_RULES[-1][2]

def is_table_free_for_party(table_or_combo, date, start_time, party_size):
    """ Convenience wrapper - predicts duration from party size/time, then checks availability. """
    duration = predict_duration(party_size, start_time)
    return is_table_free(table_or_combo, date, start_time, duration)

def find_best_single_table(date, start_time, party_size):
    """
    Return the smallest available single Table that fits the party, or None
    if nothing fits. Tables are checked in ascending max_covers order (then id,
    for a stable tie_break) so the tightest fit always wins - avoids seating a party of 2 at
    an 8-top when a 2-top is free.
    """
    candidates = Table.objects.filter(
        is_active=True,
        min_covers__lte=party_size,
        max_covers__gte=party_size,
    ).order_by('max_covers', 'id')

    for table in candidates:
        if is_table_free_for_party(table, date, start_time, party_size):
            return table
    return None