from datetime import datetime, timedelta
from django.utils import timezone

from .models import Service, SpecialHours

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